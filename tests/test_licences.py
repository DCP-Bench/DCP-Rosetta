"""evaluation.licences: declaration, machine configuration, run-time binding and redaction.

No engine or solver is needed: engines run against faked processes, as in test_engine.
"""
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch

from evaluation import engine, execution, licences
from evaluation.engine import Run
from evaluation.results import EvaluationError
from generation import manage, next_work, readiness
from tests.test_engine import FakeProcesses, Pool

KEY = "LICENSE_KEY = 0123-4567-89ab-cdef"
SPEC = {"id": "demo", "kind": "file", "target": "/run/licence/license.dat",
        "env": {"DEMO_LICENSE": "/run/licence/license.dat"}, "without": "unavailable",
        "errors": ["Cannot open licence"]}
METADATA = {"id": "demo", "image": "dcp-eval/demo:v1", "extension": ".py", "licence": SPEC}


class Machine(unittest.TestCase):
    """A licence file outside the repository and an empty saved configuration."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)
        self.licence = self.home / "license.dat"
        self.licence.write_text(f"# demo licence\n{KEY}\nEXPIRES = 2099-01-01\n")
        self.licence.chmod(0o600)
        self.config = patch.object(licences, "CONFIG", self.home / "licences.json")
        self.config.start()
        self.env = patch.dict(os.environ, {})
        self.env.start()
        os.environ.pop("DCP_LICENCE_DEMO", None)

    def tearDown(self):
        self.env.stop()
        self.config.stop()
        self.temp.cleanup()

    def use(self, value):
        os.environ["DCP_LICENCE_DEMO"] = str(value)


class DeclarationTests(unittest.TestCase):
    def test_a_complete_declaration_is_valid(self):
        self.assertEqual(licences.problems(SPEC), [])

    def test_bad_declarations_are_named(self):
        self.assertTrue(licences.problems({**SPEC, "kind": "dongle"}))
        self.assertTrue(licences.problems({**SPEC, "target": "/opt/license.dat"}))
        self.assertTrue(licences.problems({**SPEC, "errors": []}))
        self.assertTrue(licences.problems({**SPEC, "kind": "server"}))  # no port
        self.assertEqual(licences.problems({**SPEC, "kind": "server", "port": 41954}), [])
        self.assertTrue(licences.problems({**SPEC, "extra": 1}))

    def test_an_integration_without_a_declaration_needs_nothing(self):
        self.assertIsNone(licences.resolve({"id": "free"}))
        self.assertIsNone(licences.require({"id": "free"}))
        self.assertIsNone(licences.edition({"id": "free"}))


class ResolutionTests(Machine):
    def test_unconfigured_stops_a_run_before_it_starts(self):
        with self.assertRaises(EvaluationError) as caught:
            licences.require(METADATA)
        self.assertEqual(caught.exception.reason, "licence_unavailable")
        self.assertIn("evaluation.licences set demo", caught.exception.detail)

    def test_the_environment_overrides_the_saved_path(self):
        other = self.home / "other.dat"
        other.write_text("x")
        other.chmod(0o600)
        licences.CONFIG.write_text(json.dumps({"demo": str(other)}))
        self.assertEqual(licences.resolve(METADATA).source, other.resolve())
        self.use(self.licence)
        self.assertEqual(licences.resolve(METADATA).source, self.licence.resolve())
        self.assertEqual(licences.edition(METADATA), "licensed")

    def test_none_runs_the_solver_without_it(self):
        self.use("none")
        licence = licences.require(METADATA)
        self.assertTrue(licence.forced_off)
        self.assertIsNone(licence.source)

    def test_a_file_others_can_read_is_used_with_a_warning(self):
        """A system-wide install (Hexaly's /opt/hexaly_*/license.dat) is world-readable."""
        self.licence.chmod(0o644)
        self.use(self.licence)
        self.assertEqual(licences.require(METADATA).source, self.licence.resolve())
        self.assertIn("readable by every user", licences.exposed(self.licence))
        self.licence.chmod(0o600)
        self.assertIsNone(licences.exposed(self.licence))

    @unittest.skipIf(os.geteuid() == 0, "root reads every file")
    def test_a_file_this_user_cannot_read_is_refused(self):
        self.licence.chmod(0o000)
        self.use(self.licence)
        self.assertIn("not readable", licences.resolve(METADATA).reason)
        self.licence.chmod(0o600)

    def test_a_file_inside_the_repository_is_refused(self):
        with tempfile.NamedTemporaryFile(dir=execution.ROOT, suffix=".dat") as inside:
            os.chmod(inside.name, 0o600)
            self.use(inside.name)
            self.assertIn("inside the repository", licences.resolve(METADATA).reason)

    def test_a_size_limited_edition_runs_without_it(self):
        metadata = {**METADATA, "licence": {**SPEC, "without": "size-limited"}}
        self.assertIsNone(licences.require(metadata).source)
        self.assertEqual(licences.edition(metadata), "size-limited")

    def test_set_records_the_path_and_never_the_content(self):
        self.assertEqual(licences.main(["set", "demo", str(self.licence)]), 0)
        saved = licences.CONFIG.read_text()
        self.assertIn(str(self.licence.resolve()), saved)
        self.assertNotIn(KEY, saved)


class SupplyTests(Machine):
    def test_a_file_is_bound_with_its_variables_and_redacted(self):
        self.use(self.licence)
        with licences.supply(METADATA) as mount:
            [(copy, target)] = mount.binds
            self.assertEqual(target, "/run/licence/license.dat")
            self.assertEqual(copy.read_text(), self.licence.read_text())
            self.assertEqual(copy.stat().st_mode & 0o777, 0o644)  # the container's user reads it
            self.assertEqual(copy.parent.stat().st_mode & 0o777, 0o700)  # no other host user does
            self.assertEqual(mount.env, {"DEMO_LICENSE": "/run/licence/license.dat"})
        self.assertFalse(copy.exists())
        text = mount.redact(f"model printed:\n{KEY}\nfrom {self.licence.resolve()}\nEXPIRES = 2099-01-01\nok")
        self.assertNotIn("0123-4567", text)
        self.assertNotIn(str(self.licence.resolve()), text)
        self.assertNotIn("2099-01-01", text)
        self.assertIn("ok", text)
        self.assertIn(licences.REDACTED, text)

    def test_a_value_quoted_alone_is_redacted(self):
        """Gurobi quotes one value of a named-user licence: 'HostID mismatch (licensed to f00dfee, ...)'."""
        self.licence.write_text("# see GRB_LICENSE_FILE in the manual\nTYPE=NUMBERED\nHOSTID=f00dfee\nUSERNAME=someone\nKEY: AbCdEf123456789\nVERSION=13\n")
        self.use(self.licence)
        with licences.supply(METADATA) as mount:
            pass
        text = mount.redact("Gurobi error 10009: HostID mismatch (licensed to f00dfee, hostid is 0) for someone, "
                            "key AbCdEf123456789, version 13")
        for secret in ("f00dfee", "someone", "AbCdEf123456789"):
            self.assertNotIn(secret, text)
        self.assertIn("version 13", text)  # short values are left alone
        self.assertNotIn("GRB_LICENSE_FILE", " ".join(licences.secret_lines(self.licence)))  # comments too

    def test_nothing_is_bound_without_a_licence(self):
        self.use("none")
        with licences.supply(METADATA) as mount:
            self.assertIsNone(mount)

    def test_a_server_licence_is_relayed_without_network(self):
        server = socket.socket()
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]

        def answer():
            connection, _ = server.accept()
            connection.sendall(connection.recv(64).upper())
            connection.close()
        threading.Thread(target=answer, daemon=True).start()
        self.licence.write_text(f"TOKENSERVER=127.0.0.1\nPORT={port}\n")
        self.use(self.licence)
        metadata = {**METADATA, "licence": {**SPEC, "kind": "server", "port": 41954,
                                            "target": "/run/licence/gurobi.lic"}}
        with licences.supply(metadata) as mount:
            binds = {target: source for source, target in mount.binds}
            client = Path(binds["/run/licence/gurobi.lic"]).read_text()
            self.assertIn("TOKENSERVER=127.0.0.1", client)
            self.assertEqual(mount.env["DCP_LICENCE_RELAY"], "/run/licence/relay/socket")
            relay = socket.socket(socket.AF_UNIX)
            relay.connect(str(Path(binds["/run/licence/relay"]) / "socket"))
            relay.sendall(b"token please")
            self.assertEqual(relay.recv(64), b"TOKEN PLEASE")
            relay.close()
        self.assertFalse(Path(binds["/run/licence/relay"]).exists())
        server.close()


class EngineTests(Machine):
    def mount(self):
        return licences.Mount(None, [(Path("/srv/licences/license.dat"), "/run/licence/license.dat")],
                              {"DEMO_LICENSE": "/run/licence/license.dat"}, [])

    def test_docker_binds_read_only_and_keeps_no_network(self):
        fake = FakeProcesses({"docker inspect": (0, "false\n", "")})
        with patch.object(engine, "run_process", fake):
            engine.Docker().run(METADATA, "sha256:" + "ab" * 32, Path("/stage"), memory_mb=256, cpus=1, timeout=9,
                                licence=self.mount())
        command = fake.calls[0]
        self.assertIn("--mount=type=bind,source=/srv/licences/license.dat,target=/run/licence/license.dat,readonly",
                      command)
        self.assertIn("--env=DEMO_LICENSE=/run/licence/license.dat", command)
        self.assertIn("--network=none", command)
        self.assertEqual(command[-1], "sha256:" + "ab" * 32)

    def test_a_run_without_a_licence_binds_nothing(self):
        fake = FakeProcesses({"docker inspect": (0, "false\n", "")})
        with patch.object(engine, "run_process", fake):
            engine.Docker().run(METADATA, "sha256:x", Path("/stage"), memory_mb=256, cpus=1, timeout=9)
        self.assertFalse([word for word in fake.calls[0] if "licence" in word])


class ApptainerEngineTests(Pool):
    def test_apptainer_binds_read_only(self):
        (self.root / "images").mkdir()
        (self.root / "images" / "demo.sif").write_bytes(b"sif")
        mount = licences.Mount(None, [(Path("/srv/licences/license.dat"), "/run/licence/license.dat")],
                               {"DEMO_LICENSE": "/run/licence/license.dat"}, [])
        fake = FakeProcesses({"systemd-run": (0, "", ""),
                              "systemctl --user show": (0, "Result=success\nLoadState=not-found\n", "")})
        with patch.dict(os.environ, {"DCP_APPTAINER_IMAGES": str(self.root / "images")}), \
                patch.object(engine, "run_process", fake), \
                patch.object(engine, "delegated_controllers", return_value={"cpu", "memory"}):
            engine.Apptainer().run(METADATA, "sha256:x", Path("/stage"), memory_mb=256, cpus=1, timeout=9,
                                   licence=mount)
        command = fake.calls[0]
        self.assertIn("/srv/licences/license.dat:/run/licence/license.dat:ro", command)
        self.assertEqual(command[command.index("DEMO_LICENSE=/run/licence/license.dat") - 1], "--env")
        self.assertEqual(command[command.index("--network") + 1], "none")


class FakeEngine:
    """Answers every run with fixed output, and keeps the licence it was given."""

    def __init__(self, code, stdout, stderr):
        self.answer, self.licence = Run(code, stdout, stderr, False), "unset"

    def run(self, metadata, image, staging, *, licence=None, **_limits):
        self.licence = licence
        return self.answer


class ExecuteTests(Machine):
    def execute(self, fake):
        with tempfile.NamedTemporaryFile(suffix=".py") as model, \
                patch.object(execution, "_engine", return_value=fake):
            return execution.execute(model.name, {}, METADATA, "sha256:x", solution_limit=1, execution_timeout=5,
                                     compilation_timeout=5, memory_mb=256, cpus=1)

    def test_a_model_that_prints_the_licence_leaks_nothing(self):
        self.use(self.licence)
        status = json.dumps({"type": "status", "status": "error", "detail": KEY})
        fake = FakeEngine(0, f"{status}\n", f"dumped {KEY} from {self.licence.resolve()}")
        records, timing = self.execute(fake)
        self.assertIsNotNone(fake.licence)
        self.assertEqual(records[-1]["detail"], licences.REDACTED)
        self.assertNotIn("0123-4567", timing["stderr"])
        self.assertNotIn(str(self.licence.resolve()), timing["stderr"])

    def test_the_solvers_refusal_is_licence_unavailable(self):
        self.use("none")
        fake = FakeEngine(1, "", "Traceback ...\nError: Cannot open licence file")
        with self.assertRaises(EvaluationError) as caught:
            self.execute(fake)
        self.assertEqual(caught.exception.reason, "licence_unavailable")

    def test_any_message_naming_a_licence_counts(self):
        """Hexaly's message for an expired licence matched none of the declared substrings."""
        self.assertTrue(licences.licence_error(METADATA, "ERROR [hx_create_optimizer]: This license is no longer valid."))
        self.assertTrue(licences.licence_error(METADATA, "", "Licence check failed"))
        self.assertFalse(licences.licence_error(METADATA, "Int boundaries are inconsistent"))
        self.assertFalse(licences.licence_error({"id": "free"}, "invalid license"))  # declares none

    def test_unconfigured_never_starts_a_container(self):
        fake = FakeEngine(0, "", "")
        with self.assertRaises(EvaluationError) as caught:
            self.execute(fake)
        self.assertEqual(caught.exception.reason, "licence_unavailable")
        self.assertEqual(fake.licence, "unset")


class GenerationTests(unittest.TestCase):
    def test_readiness_requires_the_licence_missing_check(self):
        base = {"id": "demo", "enumeration": True}
        self.assertNotIn("licence_missing", readiness._required(base))
        self.assertIn("licence_missing", readiness._required({**base, "licence": SPEC}))

    def test_next_work_holds_back_an_integration_without_its_licence(self):
        folders = {"demo": Path("/nonexistent/solvers/demo")}
        with patch.object(next_work, "integration_folders", return_value=folders), \
                patch.object(next_work, "integration", return_value=METADATA), \
                patch.object(next_work, "solver_skill", return_value=("dcp-demo", None)), \
                patch.object(next_work, "licence_available", return_value=(False, "no demo licence")):
            [record] = next_work.integrations()
        self.assertFalse(record["ready"])
        self.assertTrue(record["licence_pending"])
        self.assertIn("Licence pending", record["blocker"])


class ManageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "skills" / "demo").mkdir(parents=True)
        (self.root / "skills" / "demo" / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
        (self.root / "model.py").write_text("model", encoding="utf-8")
        (self.root / "solvers" / "solver").mkdir(parents=True)
        (self.root / "solvers" / "CONTRACT.md").write_text("# Contract\n", encoding="utf-8")
        (self.root / "solvers" / "solver" / "CONTRACT.md").write_text("# solver\n", encoding="utf-8")
        for patcher in (patch.multiple(manage, REPO_ROOT=self.root, RUNS_ROOT=self.root / "generation" / "runs",
                                       GENERATED_ROOT=self.root / "generated_models"),
                        patch.object(manage, "_readiness", return_value={"recipe": "sha256:test"})):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(self.temp.cleanup)
        manage.init("run1")

    def attempt(self):
        return manage.attempt("run1", "problem", "solver", str(self.root / "skills" / "demo"),
                              "claude-code (claude-haiku-5-5)")

    def test_no_attempt_opens_while_the_licence_is_pending(self):
        with patch.object(manage, "licence_available", return_value=(False, "no demo licence")), \
                self.assertRaisesRegex(manage.ManagementError, "Licence pending"):
            self.attempt()

    def test_a_refused_licence_does_not_use_up_the_attempt(self):
        attempt = self.attempt()
        refused = {"accepted": False, "reason": "licence_unavailable", "detail": "expired"}
        with patch("generation.manage.evaluate_model", return_value=refused):
            result = manage.evaluate(str(attempt), str(self.root / "model.py"))
        self.assertEqual(result["reason"], "licence_unavailable")
        self.assertFalse((attempt / "evaluation.json").exists())
        self.assertTrue((attempt / "coordinator_failures" / "001.json").is_file())


class RepositoryTests(unittest.TestCase):
    def test_no_configured_licence_is_committed(self):
        """Whatever this machine's licences say appears in no tracked file."""
        configured = {**licences.saved(), **{name[len("DCP_LICENCE_"):].lower(): value
                                             for name, value in os.environ.items() if name.startswith("DCP_LICENCE_")}}
        secrets = set()
        for licence_id, value in configured.items():
            path = Path(os.environ.get(licences.variable(licence_id)) or value).expanduser()
            if value != "none" and path.is_file():
                # Long lines and tokens, and shorter bare values that look like keys (letters and
                # digits: a host ID, a key). A short `KEY=value` line such as VERSION=13 is public.
                secrets |= {s for s in licences.secret_lines(path) - {str(path)}
                            if len(s) >= 16 or (len(s) >= 6 and not re.search(r"[=:\s]", s)
                                                and re.search(r"\d", s) and re.search(r"[A-Za-z]", s))}
        if not secrets:
            self.skipTest("no licence configured on this machine")
        tracked = subprocess.run(["git", "ls-files", "-z"], cwd=execution.ROOT, capture_output=True,
                                 check=True).stdout.decode().split("\0")
        for name in filter(None, tracked):
            path = execution.ROOT / name
            if not path.is_file() or path.stat().st_size > 8 << 20:
                continue
            text = path.read_bytes().decode(errors="ignore")
            leaked = sum(s in text for s in secrets)
            # The count only: printing what leaked would leak it again, into the test log.
            self.assertFalse(leaked, f"{name} holds {leaked} piece(s) of a configured licence")


if __name__ == "__main__":
    unittest.main()
