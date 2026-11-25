"""Run a FOX model (GroundFOX + a SAT solver) on a JSON instance.

A model is a Python file with two names:

    FOX = '''invocabulary { ... } outvocabulary { ... } theory { ... }'''
    def structure(instance): return {"domain": [...], "Edge": [(0, 1), ...], "p": True}

`structure` turns the instance into the interpretation of every input symbol: a
proposition is True/False, a predicate an iterable of tuples (or of single elements
for arity 1). Elements are integers or identifiers; a negative integer -k is the
element `negk` (FOX numbers have no sign), and an output value `negk` reads back as -k. The domain is the
optional "domain" entry plus every element used in an interpretation.

This file grounds the FOX text with `groundfox`, solves the CNF with CaDiCaL 3.0.0
(python-sat) and reads every output predicate back with its last argument as the
value and the others as 0-based indices: `queens(i, v)` gives queens[i] = v.

Standalone use (needs `groundfox` on PATH and `pip install python-sat`):

    python dcp_fox.py model.py instance.json [--solutions N] [--check]

where instance.json holds one instance object, or a list of them (the first is used).
"""
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_'\"-]*\Z")
ALLOWED_FLAGS = {"--nested-guards", "--functions", "--arbitrary-fol"}


class ModelError(ValueError):
    """Something in the submission (or what it returned) that the runner cannot use."""


def load(path):
    spec = importlib.util.spec_from_file_location("fox_model", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not isinstance(getattr(module, "FOX", None), str):
        raise ModelError("The model must define FOX, a string holding the invocabulary, outvocabulary and theory")
    if not callable(getattr(module, "structure", None)):
        raise ModelError("The model must define structure(instance), returning the input interpretations")
    flags = list(getattr(module, "FLAGS", []))
    bad = [f for f in flags if f not in ALLOWED_FLAGS]
    if bad:
        raise ModelError(f"FLAGS may only hold {sorted(ALLOWED_FLAGS)}; got {bad}")
    return module.FOX, module.structure, flags


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"//[^\n]*", " ", text)


def vocabulary(fox, kind):
    """Symbol -> arity of the `invocabulary` or `outvocabulary` block."""
    match = re.search(kind + r"\s*\{([^}]*)\}", strip_comments(fox))
    if not match:
        raise ModelError(f"FOX has no {kind} block")
    symbols = {}
    for name, arity, function in re.findall(r"([A-Za-z][A-Za-z0-9_'\"-]*)\s*/\s*(\d+)\s*(:?)", match.group(1)):
        symbols[name] = int(arity)
    return symbols


def element(value, where):
    if isinstance(value, bool):
        raise ModelError(f"{where}: a Boolean is not a domain element (use 0/1 or a name)")
    if isinstance(value, int):
        return str(value) if value >= 0 else f"neg{-value}"  # FOX numbers are digits only
    if isinstance(value, str) and IDENTIFIER.match(value):
        return value
    raise ModelError(f"{where}: {value!r} is not a FOX element (a non-negative integer or a name "
                     "starting with a letter)")


def structure_text(fox, data):
    if not isinstance(data, dict):
        raise ModelError("structure(instance) must return a dict")
    if re.search(r"\bstructure\s*\{", strip_comments(fox)):
        raise ModelError("FOX must not contain a structure block: structure(instance) supplies it")
    inputs = vocabulary(fox, "invocabulary")
    domain = {}
    for value in data.get("domain", []):
        domain[element(value, "domain")] = None
    lines = []
    for name, arity in inputs.items():
        if name not in data:
            raise ModelError(f"structure(instance) gives no interpretation for input symbol {name}/{arity}")
        value = data[name]
        if arity == 0:
            if not isinstance(value, bool):
                raise ModelError(f"{name}/0 is a proposition: give True or False")
            lines.append(f"    {name} = {'true' if value else 'false'}")
            continue
        tuples = []
        seen = set()
        for item in value:
            item = tuple(item) if isinstance(item, (tuple, list)) else (item,)
            if len(item) != arity:
                raise ModelError(f"{name}/{arity} got the tuple {item!r} of length {len(item)}")
            text = tuple(element(v, name) for v in item)
            for v in text:
                domain[v] = None
            if text not in seen:
                seen.add(text)
                tuples.append(text)
        body = " ; ".join("(" + ",".join(t) + ")" if arity > 1 else t[0] for t in tuples)
        lines.append(f"    {name} = {{ {body} }}" if body else f"    {name} = {{}}")
    extra = sorted(set(data) - set(inputs) - {"domain"})
    if extra:
        raise ModelError(f"structure(instance) interprets {extra}, which the invocabulary does not declare")
    if not domain:
        raise ModelError("The domain is empty: give at least one element")
    return "structure {\n    domain = { " + " ; ".join(domain) + " }\n" + "\n".join(lines) + "\n}\n"


def ground(text, flags, workdir, timeout):
    """Run groundfox; return (CNF path, {atom text: variable}, clause count). The clauses stay in
    the file: only the solver process reads them, so they are never held twice."""
    workdir = Path(workdir)
    (workdir / "model.fox").write_text(text, encoding="utf-8")
    command = ["groundfox", "-i", str(workdir / "model.fox"), "-o", str(workdir / "model.cnf"),
               "-p", str(workdir / "model.cfx"), "-t", str(workdir / "model_symbols.txt"), *flags]
    done = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    if done.returncode != 0:
        message = (done.stderr.strip() or done.stdout.strip() or f"exit code {done.returncode}")
        raise ModelError("groundfox: " + message[-2000:])
    clauses = 0
    with open(workdir / "model.cnf") as cnf:
        for line in cnf:
            if line.startswith("p cnf"):
                clauses = int(line.split()[3])
                break
    atoms = {}
    sym = workdir / "model_symbols.txt"  # the name checkfox looks for next to model.fox
    if sym.exists():
        for line in sym.read_text().splitlines():
            parts = line.split(None, 2)
            if len(parts) == 3 and parts[0] == "PRED":
                atoms[parts[2].strip()] = int(parts[1])
    return workdir / "model.cnf", atoms, clauses


def check_proof(flags, workdir, timeout):
    """Run checkfox on the grounding's proof log; return (verdict, message): valid, rejected or error."""
    workdir = Path(workdir)
    done = subprocess.run(["checkfox", "-i", str(workdir / "model.fox"), "-o", str(workdir / "model.cnf"),
                           "-p", str(workdir / "model.cfx"), *flags], capture_output=True, text=True, timeout=timeout)
    verdict = {0: "valid", 1: "rejected"}.get(done.returncode, "error")
    return verdict, (done.stderr.strip() or done.stdout.strip())[-1000:]


DIGITS = "_digits"  # an output x may be given as x_digits(indices..., position, digit), units at 0
ATOM = re.compile(r"([A-Za-z][A-Za-z0-9_'\"-]*)(?:\((.*)\))?\Z")


def output_atoms(atoms, names, outputs):
    """Per declared output: list of (variable, index tuple, value), the value being an element, or
    ("digit", position, digit) for an output given as `<name>_digits(indices..., position, digit)`."""
    found = {name: [] for name in names}
    predicate = {(name if name in outputs else name + DIGITS): name for name in names}
    for text, var in atoms.items():
        match = ATOM.match(text)
        if not match or match.group(1) not in predicate:
            continue
        pred, name = match.group(1), predicate[match.group(1)]
        args = [a.strip() for a in (match.group(2) or "").split(",") if a.strip()]
        if len(args) != outputs.get(pred, len(args)) or not args:
            continue
        if pred.endswith(DIGITS) and pred != name:
            if len(args) < 2:
                continue
            found[name].append((var, tuple(args[:-2]), ("digit", args[-2], args[-1])))
        else:
            found[name].append((var, tuple(args[:-1]), args[-1]))
    return found


def number(text, name):
    if text.startswith("neg") and text[3:].isdigit():
        return -int(text[3:])
    if not text.isdigit():
        raise ModelError(f"Output {name}: {text} is not an integer element (indices and values must be integers)")
    return int(text)


def nest(entries, name):
    if not entries[0][0]:
        if len(entries) != 1:
            raise ModelError(f"Output {name} has {len(entries)} values; give exactly one true atom")
        return entries[0][1]
    groups = {}
    for indices, value in entries:
        groups.setdefault(indices[0], []).append((indices[1:], value))
    order = sorted(groups)
    if order != list(range(len(order))):
        raise ModelError(f"Output {name}: indices must be 0-based and contiguous, got {order}")
    return [nest(groups[i], name) for i in order]


def decode(model_true, found):
    values = {}
    for name, entries in found.items():
        chosen = {}
        digits = {}
        for var, indices, value in entries:
            if var not in model_true:
                continue
            key = tuple(number(i, name) for i in indices)
            if isinstance(value, tuple):
                position, digit = number(value[1], name), number(value[2], name)
                if not 0 <= digit <= 9:
                    raise ModelError(f"Output {name}_digits{list(key)}: digit {digit} is not 0..9")
                slot = digits.setdefault(key, {})
                if position in slot:
                    raise ModelError(f"Output {name}_digits{list(key)} has two digits at position {position}: "
                                     "make it exactly one")
                slot[position] = digit
                continue
            if key in chosen:
                raise ModelError(f"Output {name}{list(key)} has two true values ({chosen[key]} and {value}): "
                                 "make it exactly one")
            chosen[key] = number(value, name)
        for key, slot in digits.items():
            chosen[key] = sum(d * 10 ** p for p, d in slot.items())
        if not chosen:
            raise ModelError(f"Output {name} has no true atom in the solution")
        values[name] = nest(sorted(chosen.items()), name)
    return values


def check_outputs(fox, names):
    outputs = vocabulary(fox, "outvocabulary")
    missing = [n for n in names if n not in outputs and n + DIGITS not in outputs]
    if missing:
        raise ModelError(f"Declared outputs {missing} are not out-predicates of the outvocabulary "
                         "(name them exactly; the value is the last argument)")
    zero = [n for n in names if outputs.get(n, outputs.get(n + DIGITS)) < (1 if n in outputs else 2)]
    if zero:
        raise ModelError(f"Outputs {zero} have arity 0; the value must be the last argument, e.g. {zero[0]}/1")
    return outputs


SOLVER = "cadical300"  # CaDiCaL 3.0.0 from python-sat


def _solver_child(conn, cnf_path, name):
    from pysat.solvers import Solver as PySolver
    solver = PySolver(name=name)
    with open(cnf_path) as cnf:
        for line in cnf:
            if line[:1] in ("c", "p", "%", "\n", ""):
                continue
            literals = [int(x) for x in line.split()]
            if literals and literals[-1] == 0:
                literals.pop()
            solver.add_clause(literals)
    conn.send("ready")
    while True:
        command, payload = conn.recv()
        if command == "solve":
            result = solver.solve()
            conn.send((result, solver.get_model() if result else None))
        elif command == "block":
            solver.add_clause(payload)
        else:
            return


class Solver:
    """An incremental SAT solver (CaDiCaL 3.0.0) in a child process, with blocking over the output atoms.

    python-sat's CaDiCaL ignores interrupt(), so the solver runs in a forked process that is
    killed when the time is up; between calls it keeps its state (incremental solving).
    """

    def __init__(self, cnf_path, name=SOLVER):
        import multiprocessing
        context = multiprocessing.get_context("fork")
        self.conn, child = context.Pipe()
        self.process = context.Process(target=_solver_child, args=(child, str(cnf_path), name), daemon=True)
        self.process.start()
        if self.conn.recv() != "ready":  # the clauses are loaded; the CNF file may now go
            raise RuntimeError("the SAT solver process failed to load the CNF")
        self.model = None

    def solve(self, seconds):
        """True, False, or None when the time ran out (the solver is then gone)."""
        self.conn.send(("solve", None))
        if not self.conn.poll(max(seconds, 0.0)):
            self.close()
            return None
        result, self.model = self.conn.recv()
        return result

    def true_vars(self):
        return {v for v in self.model if v > 0}

    def block(self, model_true, variables):
        self.conn.send(("block", [-v if v in model_true else v for v in variables]))

    def close(self):
        if self.process.is_alive():
            self.process.kill()
            self.process.join()


def main(argv):
    import argparse
    import time
    parser = argparse.ArgumentParser(description="Ground a FOX model with groundfox and solve it with CaDiCaL 3.0.0.")
    parser.add_argument("model")
    parser.add_argument("instance")
    parser.add_argument("--solutions", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--check", action="store_true", help="verify the grounding's proof log with checkfox first")
    args = parser.parse_args(argv)
    fox, build, flags = load(args.model)
    instance = json.loads(Path(args.instance).read_text())
    if isinstance(instance, list):
        instance = instance[0]
    outputs = vocabulary(fox, "outvocabulary")
    start = time.monotonic()
    with tempfile.TemporaryDirectory() as work:
        cnf, atoms, _ = ground(fox + "\n" + structure_text(fox, build(instance)), flags, work, args.timeout)
        if args.check:
            verdict, message = check_proof(flags, work, args.timeout)
            print(f"checkfox: proof {verdict}" + ("" if verdict == "valid" else f": {message}"))
            if verdict != "valid":
                return 1
        found = output_atoms(atoms, list(outputs), outputs)
        variables = sorted({v for entries in found.values() for v, _, _ in entries})
        solver = Solver(cnf)
        for count in range(args.solutions):
            result = solver.solve(args.timeout - (time.monotonic() - start))
            if result is None:
                print("timeout")
                return 1
            if not result:
                print("unsatisfiable" if count == 0 else "no more solutions")
                return 0
            truth = solver.true_vars()
            shown = {}
            for name, entries in found.items():
                try:
                    shown.update(decode(truth, {name: entries}))
                except ModelError:  # an auxiliary relation, not one value per index: list its true atoms
                    shown[name] = [[*i, v] for var, i, v in entries if var in truth]
            print(json.dumps(shown))
            solver.block(truth, variables)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
