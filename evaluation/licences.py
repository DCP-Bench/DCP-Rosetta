"""Solver licences: host files given to a container at run time, never built into an image.

    make licences                                   # status of every licensed integration
    python -m evaluation.licences set hexaly ~/.config/dcp-rosetta/licences/hexaly/license.dat
    python -m evaluation.licences check hexaly      # file checks, then a pilot solve
    python -m evaluation.licences todo              # licences still to acquire, and how
    docker run $(python -m evaluation.licences args hexaly) ... # a probe container with it

An integration that needs a licence declares it in its metadata.json:

    "licence": {"id": "hexaly", "kind": "file", "target": "/run/licence/license.dat",
                "env": {"HX_LICENSE_PATH": "/run/licence/license.dat"},
                "without": "unavailable", "errors": ["Cannot open file"]}

- `id`: the licence, shared by every binding of one solver.
- `kind`: `file` (a key file), `directory` (a licensed install, such as CPLEX Studio) or
  `server` (a licence-server client file, `TOKENSERVER=` and `PORT=` lines: the run reaches
  the server through a relay, see `Relay`, and the container keeps no network).
- `target`: where the container sees it. `env`: variables set in the container.
- `without`: `unavailable` (no run without it) or `size-limited` (a free edition runs).
- `errors`: substrings of the solver's own licence messages. A run that fails with one,
  or with any message naming a licence (`licen`, either spelling), is
  `licence_unavailable`, which says nothing about the model. The fallback is deliberate:
  a licence failure taken for a model's costs attempts and blocks pairs, while the
  reverse only withholds a verdict. (Hexaly's "This license is no longer valid" for an
  expired licence matched no substring guessed from its docs.)

Each machine says where its licences are, outside the repository: `DCP_LICENCE_<ID>`, else
`.dcp-licences.json` at the checkout root (paths only; per checkout, as `.dcp-engine.json`,
since one NFS home serves machines with different licences). With none configured, a
run that needs one stops before any container starts. `DCP_LICENCE_<ID>=none` instead
runs the solver without it, so the `licence_missing` readiness check sees what the
integration does then: the solver's own refusal as licence_unavailable, or, for a
size-limited one, its free edition at work.

The image never holds a licence, so it can be cached, exported and shipped freely. What
a run prints is redacted before it is parsed or stored: the licence's lines and its host
path become `[licence redacted]`, so a model that prints the file leaks nothing into a
record. Results name the edition only (`licensed` or `size-limited`).

Agents never read a licence file: `check` is the only command they run on one.
"""
import argparse
import contextlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import socket
import stat
import sys
import tempfile
import threading

from .execution import ROOT, integration, integration_folders
from .results import EvaluationError

CONFIG = ROOT / ".dcp-licences.json"
KINDS = ("file", "directory", "server")
WITHOUT = ("unavailable", "size-limited")
KEYS = {"id", "kind", "target", "env", "without", "errors", "port"}
REDACTED = "[licence redacted]"
RELAY_TARGET = "/run/licence/relay"
# What is redacted from a licence file: lines of at least 8 characters, and the values
# (after `=` or `:`) and long tokens in them, from 6 and 12 characters: a solver can
# quote one value alone, as Gurobi does with HOSTID in "HostID mismatch (licensed to ...)".
SHORTEST_LINE, SHORTEST_VALUE, SHORTEST_TOKEN = 8, 6, 12
LICENCE_ID = re.compile(r"^[a-z0-9_]+$")
LICENCE_WORD = re.compile(r"licen[cs]", re.IGNORECASE)
GUIDE = "LICENCE.md"


# ---- Declarations -----------------------------------------------------------------------

def problems(spec):
    """What is wrong with a metadata `licence` declaration; empty when it is valid."""
    if not isinstance(spec, dict):
        return ["licence must be an object"]
    found = []
    if set(spec) - KEYS:
        found.append(f"unknown licence keys {sorted(set(spec) - KEYS)}")
    if not isinstance(spec.get("id"), str) or not LICENCE_ID.match(spec.get("id") or ""):
        found.append("licence.id must be lowercase letters, digits and underscores")
    if spec.get("kind") not in KINDS:
        found.append(f"licence.kind must be one of {', '.join(KINDS)}")
    target = spec.get("target")
    if not isinstance(target, str) or not target.startswith("/run/licence/") or any(c in target for c in ",:"):
        found.append("licence.target must be a path under /run/licence/, without ',' or ':'")
    env = spec.get("env", {})
    if not isinstance(env, dict) or not all(isinstance(k, str) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", k)
                                            and isinstance(v, str) for k, v in env.items()):
        found.append("licence.env must map variable names to strings")
    if spec.get("without") not in WITHOUT:
        found.append(f"licence.without must be one of {', '.join(WITHOUT)}")
    errors = spec.get("errors")
    if not isinstance(errors, list) or not errors or not all(isinstance(e, str) and e for e in errors):
        found.append("licence.errors must list the solver's licence messages (substrings)")
    if spec.get("kind") == "server" and not (type(spec.get("port")) is int and 0 < spec["port"] < 65536):
        found.append("a server licence needs the server's default port as licence.port")
    return found


def declared(metadata):
    """An integration's licence declaration, or None when it needs none."""
    spec = metadata.get("licence")
    if spec is None:
        return None
    found = problems(spec)
    if found:
        raise EvaluationError("infrastructure_error", f"{metadata.get('id')}: {'; '.join(found)}")
    return spec


# ---- This machine's configuration -------------------------------------------------------

def saved():
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, ValueError):
        return {}


def variable(licence_id):
    return f"DCP_LICENCE_{licence_id.upper()}"


def configured(licence_id):
    """The path this machine gives for a licence, `none` when forced off, or None."""
    return os.environ.get(variable(licence_id)) or saved().get(licence_id) or None


def _inside_repository(path):
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False


def unusable(path, kind):
    """Why a configured licence path cannot be used, or None."""
    if any(c in str(path) for c in ",:"):
        return f"{path}: a licence path must not contain ',' or ':' (they separate mount options)"
    if not path.exists():
        return f"{path} does not exist"
    if _inside_repository(path):
        return f"{path} is inside the repository; keep licences outside it (~/.config/dcp-rosetta/licences/)"
    if kind == "directory":
        return None if path.is_dir() else f"{path} is not a directory"
    if not path.is_file():
        return f"{path} is not a file"
    if not os.access(path, os.R_OK):
        return f"{path} is not readable by {os.environ.get('USER', 'this user')}"
    return None


def exposed(path):
    """A warning when other users of this machine can read a licence file, or None.

    Not a refusal: a solver installed system-wide keeps its licence world-readable (Hexaly's
    /opt/hexaly_*/license.dat), and who may read it there is the administrator's call.
    """
    try:
        if path.is_file() and path.stat().st_mode & stat.S_IROTH:
            return f"{path} is readable by every user of this machine; a copy of your own at mode 600 is safer"
    except OSError:
        pass
    return None


class Licence:
    """One integration's licence on this machine: `source` is None when it is missing."""

    def __init__(self, spec, source, reason, forced_off=False):
        self.spec, self.source, self.reason, self.forced_off = spec, source, reason, forced_off

    @property
    def id(self):
        return self.spec["id"]

    @property
    def edition(self):
        if self.source:
            return "licensed"
        return "size-limited" if self.spec["without"] == "size-limited" else None


def resolve(metadata):
    """None when the integration needs no licence, else its `Licence` here."""
    spec = declared(metadata)
    if spec is None:
        return None
    value = configured(spec["id"])
    if not value:
        return Licence(spec, None, f"no {spec['id']} licence configured on this machine: "
                                   f"`python -m evaluation.licences set {spec['id']} PATH` "
                                   f"(or {variable(spec['id'])}); see `python -m evaluation.licences todo`")
    if value == "none":
        return Licence(spec, None, f"{variable(spec['id'])}=none", forced_off=True)
    path = Path(value).expanduser()
    reason = unusable(path, spec["kind"])
    return Licence(spec, None if reason else path.resolve(), reason)


def require(metadata):
    """The licence a run uses (None when it needs or has none); raises licence_unavailable
    when the integration cannot run without one and this machine has none (unless it was
    switched off on purpose, to run the solver unlicensed)."""
    licence = resolve(metadata)
    if (licence is not None and licence.source is None and not licence.forced_off
            and licence.spec["without"] == "unavailable"):
        raise EvaluationError("licence_unavailable", f"{metadata['id']} needs a licence: {licence.reason}")
    return licence


def edition(metadata):
    licence = resolve(metadata)
    return licence.edition if licence else None


def available(solver_id):
    """(usable, reason): whether this machine can run the integration as far as licences go.
    An integration that cannot be read is not a licence matter: other gates report it."""
    try:
        metadata = integration(solver_id)
    except (EvaluationError, OSError, ValueError, KeyError):
        return True, None
    try:
        licence = resolve(metadata)
    except EvaluationError as error:
        return False, error.detail
    if licence is None or licence.source or licence.spec["without"] == "size-limited":
        return True, None
    return False, licence.reason


def licence_error(metadata, *texts):
    """Whether a failed run of a licensed integration names its licence: one of its declared
    messages, or any mention of a licence (`licen`, licence or license, any case)."""
    spec = metadata.get("licence")
    if not isinstance(spec, dict):
        return False
    patterns = [pattern for pattern in spec.get("errors", []) if isinstance(pattern, str) and pattern]
    return any(pattern in (text or "") for pattern in patterns for text in texts) or \
        any(LICENCE_WORD.search(text or "") for text in texts)


# ---- Supplying a licence to one run -----------------------------------------------------

class Mount:
    """What one run gets: read-only binds, environment variables, and what to redact."""

    def __init__(self, licence, binds, env, secrets):
        self.licence, self.binds, self.env = licence, binds, env
        # Longest first, so a line is redacted before a shorter line inside it.
        self.secrets = sorted({s for s in secrets if len(s) >= SHORTEST_VALUE}, key=len, reverse=True)

    def redact(self, text):
        if not text:
            return text
        for secret in self.secrets:
            text = text.replace(secret, REDACTED)
        return text


def secret_lines(path):
    """What of a licence file to redact: its lines, their values and long tokens, and its path."""
    found = {str(path)}
    try:
        lines = path.read_text(errors="replace").splitlines() if path.is_file() and path.stat().st_size <= 1 << 20 else []
    except OSError:
        lines = []
    for line in (line.strip() for line in lines):
        if line.startswith(("#", "!", "//", ";")):
            continue  # a comment is the vendor's boilerplate, not the licence
        if len(line) >= SHORTEST_LINE:
            found.add(line)
        separator = min((i for i in (line.find("="), line.find(":")) if i > 0), default=-1)
        if separator > 0:
            value = line[separator + 1:].strip().strip("\"'")
            if len(value) >= SHORTEST_VALUE:
                found.add(value)
        found.update(token for token in re.split(r"[\s=:,;\"']+", line) if len(token) >= SHORTEST_TOKEN)
    return found


def server_address(path, default_port):
    """TOKENSERVER (or SERVER) and PORT from a licence-server client file."""
    values = {}
    for line in path.read_text(errors="replace").splitlines():
        key, _, value = line.partition("=")
        if value:
            values[key.strip().upper()] = value.strip()
    host = values.get("TOKENSERVER") or values.get("SERVER")
    if not host:
        raise EvaluationError("licence_unavailable", "the server licence file names no TOKENSERVER")
    host = host.split(",")[0].strip()
    port = int(values.get("PORT", default_port))
    return host, port, {k: v for k, v in values.items() if k not in ("TOKENSERVER", "SERVER", "PORT")}


class Relay:
    """A Unix socket in a fresh directory, forwarded to a licence server.

    The container keeps --network=none: it gets the directory as /run/licence/relay, and
    its runner forwards 127.0.0.1:PORT to the socket (runner/licence_relay.py).
    """

    def __init__(self, host, port):
        self.address = (host, port)
        # Bound as a directory, so its mode is what the container sees: it holds only the socket.
        self.directory = Path(tempfile.mkdtemp(prefix="dcp_relay_"))
        self.directory.chmod(0o755)
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(str(self.directory / "socket"))
        # The container's user is not this one: it must be able to connect.
        (self.directory / "socket").chmod(0o777)
        self.server.listen(16)
        self.thread = threading.Thread(target=self._accept, daemon=True)
        self.thread.start()

    def _accept(self):
        while True:
            try:
                client, _ = self.server.accept()
            except OSError:
                return
            threading.Thread(target=self._serve, args=(client,), daemon=True).start()

    def _serve(self, client):
        try:
            upstream = socket.create_connection(self.address, timeout=15)
        except OSError:
            client.close()
            return
        upstream.settimeout(None)
        for source, sink in ((client, upstream), (upstream, client)):
            threading.Thread(target=_pump, args=(source, sink), daemon=True).start()

    def close(self):
        self.server.close()
        shutil.rmtree(self.directory, ignore_errors=True)


def _pump(source, sink):
    try:
        while chunk := source.recv(65536):
            sink.sendall(chunk)
    except OSError:
        pass
    finally:
        for end in (source, sink):
            with contextlib.suppress(OSError):
                end.shutdown(socket.SHUT_RDWR)


@contextlib.contextmanager
def supply(metadata):
    """The `Mount` for one run of this integration, or None when it runs without a licence.
    Raises licence_unavailable before any container starts when it cannot.

    A licence file is bound as a per-run copy the container's user can read (it is not the
    invoking user under Docker and podman), kept in a private 0700 directory: a bind
    mount ignores the host directory's mode, so no other host user can reach the copy.
    """
    licence = require(metadata)
    if licence is None or licence.source is None:
        yield None
        return
    spec = licence.spec
    secrets = secret_lines(licence.source)
    env = dict(spec.get("env", {}))
    if spec["kind"] == "directory":
        yield Mount(licence, [(licence.source, spec["target"])], env, secrets)
        return
    private = Path(tempfile.mkdtemp(prefix="dcp_licence_"))
    relay = None
    try:
        copy = private / "licence"
        if spec["kind"] == "file":
            shutil.copyfile(licence.source, copy)
            binds = [(copy, spec["target"])]
        else:
            host, port, rest = server_address(licence.source, spec["port"])
            secrets.add(host)
            relay = Relay(host, port)
            # The client file the container sees points at its own loopback forwarder.
            copy.write_text("".join(f"{k}={v}\n" for k, v in rest.items()) + f"TOKENSERVER=127.0.0.1\nPORT={port}\n")
            env.update(DCP_LICENCE_RELAY=f"{RELAY_TARGET}/socket", DCP_LICENCE_PORT=str(port))
            binds = [(relay.directory, RELAY_TARGET), (copy, spec["target"])]
        copy.chmod(0o644)
        yield Mount(licence, binds, env, secrets)
    finally:
        if relay:
            relay.close()
        shutil.rmtree(private, ignore_errors=True)


# ---- Command line -----------------------------------------------------------------------

def licensed():
    """{licence id: [(integration id, folder, spec)]} over every integration that declares one."""
    found = {}
    for solver_id, folder in integration_folders(ROOT).items():
        try:
            spec = declared(integration(solver_id))
        except (EvaluationError, OSError, ValueError, KeyError):
            continue
        if spec:
            found.setdefault(spec["id"], []).append((solver_id, folder, spec))
    return found


def guide(folder):
    """The human instructions for acquiring a licence: LICENCE.md beside the solver's skill."""
    for candidate in (folder.parent / GUIDE, folder / GUIDE):
        if candidate.is_file():
            return candidate.relative_to(ROOT).as_posix()
    return None


def _status(licence_id, users):
    value = configured(licence_id)
    if not value:
        return "missing", "not configured"
    if value == "none":
        return "off", f"{variable(licence_id)}=none"
    path = Path(value).expanduser()
    reason = unusable(path, users[0][2]["kind"])
    if reason:
        return "unusable", reason
    return "configured", exposed(path) or "configured"


def command_status(_args):
    users = licensed()
    if not users:
        print("No integration declares a licence.")
        return 0
    for licence_id, entries in sorted(users.items()):
        state, detail = _status(licence_id, entries)
        names = ", ".join(solver_id for solver_id, _, _ in entries)
        without = entries[0][2]["without"]
        print(f"{licence_id:16} {state:10} {names}  (without it: {without}){'' if state == 'configured' else '  ' + detail}")
    return 0


def command_todo(_args):
    pending = 0
    for licence_id, entries in sorted(licensed().items()):
        state, detail = _status(licence_id, entries)
        if state == "configured":
            continue
        pending += 1
        instructions = guide(entries[0][1]) or "(no LICENCE.md yet)"
        print(f"{licence_id}: {detail}; used by {', '.join(e[0] for e in entries)}\n"
              f"  1. get it: {instructions}\n"
              f"  2. store it outside the repository, e.g. ~/.config/dcp-rosetta/licences/{licence_id}/, chmod 600\n"
              f"  3. python -m evaluation.licences set {licence_id} PATH\n"
              f"  4. python -m evaluation.licences check {licence_id}")
    if not pending:
        print("No licence to acquire: every declared licence is configured here.")
    return 0


def command_set(args):
    users = licensed().get(args.licence)
    kind = users[0][2]["kind"] if users else ("directory" if Path(args.path).expanduser().is_dir() else "file")
    path = Path(args.path).expanduser().resolve()
    reason = unusable(path, kind)
    if reason:
        print(f"evaluation.licences: {reason}", file=sys.stderr)
        return 1
    if exposed(path):
        print(f"evaluation.licences: warning: {exposed(path)}", file=sys.stderr)
    config = saved()
    config[args.licence] = str(path)
    CONFIG.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    print(f"{args.licence}: {path} (saved in {CONFIG.name})"
          + ("" if users else "; no integration declares this licence yet"))
    return 0


def _pilot(solver_id):
    """The integration's pilot fixture, when tests/test_solvers.py registers one."""
    try:
        from tests.test_solvers import PILOTS
        from tests.test_evaluation import SOURCE
    except ImportError:
        return None, None
    name = PILOTS.get(solver_id)
    return (ROOT / "tests" / "fixtures" / name, SOURCE) if name else (None, None)


def command_check(args):
    users = licensed()
    chosen = {args.licence: users.get(args.licence, [])} if args.licence else users
    failed = False
    for licence_id, entries in sorted(chosen.items()):
        if not entries:
            print(f"{licence_id}: no integration declares this licence")
            failed = True
            continue
        state, detail = _status(licence_id, entries)
        if state != "configured":
            print(f"FAIL  {licence_id}: {detail}; see `python -m evaluation.licences todo`")
            failed = True
            continue
        print(f"PASS  {licence_id}: file")
        for solver_id, _, _ in entries:
            fixture, source = _pilot(solver_id)
            if fixture is None or args.files_only:
                print(f"SKIP  {solver_id}: no pilot fixture to solve yet" if fixture is None else
                      f"SKIP  {solver_id}: --files-only")
                continue
            from .check import evaluate
            result = evaluate(fixture, "tiny", solver_id, reference_source=source,
                              instances=[{"n": 3, "optimize": False}])
            ok = result.get("accepted")
            failed |= not ok
            print(f"{'PASS' if ok else 'FAIL'}  {solver_id}: pilot solve"
                  + ("" if ok else f" ({result.get('reason')}: {str(result.get('detail', ''))[:300]})"))
    return 1 if failed else 0


def command_args(args):
    """`docker run` flags that give a probe or toy-test container the licence, as the evaluator
    would (read-only, with its variables). Such containers run as the image's root, which can
    read the 0600 file, so the original is bound."""
    entries = licensed().get(args.licence)
    if not entries:
        print(f"evaluation.licences: no integration declares licence {args.licence}", file=sys.stderr)
        return 1
    spec = entries[0][2]
    value = configured(args.licence)
    path = Path(value).expanduser() if value and value != "none" else None
    reason = unusable(path, spec["kind"]) if path else "not configured"
    if reason or spec["kind"] == "server":
        print(f"evaluation.licences: {args.licence}: "
              f"{reason or 'a server licence is relayed by the evaluator only; use evaluation.check'}", file=sys.stderr)
        return 1
    flags = ["-v", f"{path.resolve()}:{spec['target']}:ro"]
    for key, value in spec.get("env", {}).items():
        flags += ["-e", f"{key}={value}"]
    print(" ".join(shlex.quote(flag) for flag in flags))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("status", help="the licensed integrations and whether this machine has their licences")
    commands.add_parser("todo", help="the licences still to acquire, with the steps")
    set_p = commands.add_parser("set", help="record where a licence is (the file is never read)")
    set_p.add_argument("licence")
    set_p.add_argument("path")
    check_p = commands.add_parser("check", help="check a configured licence, then solve each pilot with it")
    check_p.add_argument("licence", nargs="?")
    check_p.add_argument("--files-only", action="store_true", help="skip the pilot solves")
    args_p = commands.add_parser("args", help="docker run flags giving a probe container the licence")
    args_p.add_argument("licence")
    args = parser.parse_args(argv)
    handler = {"todo": command_todo, "set": command_set, "check": command_check,
               "args": command_args}.get(args.command, command_status)
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
