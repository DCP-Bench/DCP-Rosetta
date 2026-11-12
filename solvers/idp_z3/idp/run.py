"""Runner protocol for the idp_z3 integration. Runs inside the image only.

The instance binding (the structure generated from the JSON instance, described next) is in dcp_convert_idp.py: a
separate file because readers download it to add data to their own model; the runner imports it, so both bind
identically.

A submission is a plain FO(.) knowledge base (`vocabulary` + `theory`, optionally
its own `structure`), not a program, and is parsed as written. All instance data
arrives in a `structure` the runner generates, which is how FO(.) hands data to a
knowledge base. FO(.) type ranges must be integer literals, so that structure also
interprets the types the data sizes:

- Every instance field whose name matches a declared symbol is interpreted: a
  scalar as `n := 5.`, an array as `cost := {(0,0)->1, ...}.` with 0-based
  indices, a Boolean array as the set of its true tuples.
- An argument type of such a symbol that is declared `<: Int` and interpreted
  nowhere is sized from the array: `type Task <: Int` with `cost: Task * Person
  -> Int` and a 4x5 `cost` gives `Task := {0..3}. Person := {0..4}.`
- A type `Range_f` declared `<: Int` and interpreted nowhere, for an integer scalar
  field `f`, is `{1..f}`: `type Range_n <: Int` with `n: 8` gives `Range_n := {1..8}.`
- Any other such type `T` with a declared constant `T_size: () -> Int` is `{1..v}`,
  where `v` is the value the theory gives `T_size` from the data
  (`T_size() = 2 * k().`). The runner reads it from IDP-Z3's own simplification of
  the theory, with `T` provisionally empty, before solving.

An output declared as a partial function, `diffs: Range_n -> Int (domain: gap)`, is
read only on the argument tuples where its domain predicate holds, so its length can
be shorter than its argument type.
- A ragged list of rows `F` binds padded with 0 (false) to the longest row, as a
  rectangular `F`, plus `F_len` with each row's real length. A list of mixed rows
  such as `[target, [cells...]]` binds one piece per column, `F_1`, `F_2`, ... (see
  `pieces`). Only the names a model declares are bound; a string is refused only in
  a declared field.

A nullary `minimize: () -> Int` or `maximize: () -> Int` makes it an optimization.

The runner drives `theory.solver` (a z3.Solver) and `theory.optimize_solver` (a
z3.Optimize) itself rather than calling `Theory.expand` / `Theory.optimize`:
`expand` blocks on every unknown atom, so auxiliary symbols multiply the models,
and treats a z3 `unknown` like `unsat`; `optimize` raises the same AssertionError
for an unsatisfiable theory and for a timeout. Here only the declared outputs are
blocked, and `unknown` is always reported as a timeout, never as exhaustion.
"""
import contextlib
import json
from pathlib import Path
import re
import signal
import sys
import time

# The engine prints diagnostics to stdout, which is also the protocol channel. The
# protocol keeps the original stdout; everything else goes to stderr. Only the runner
# (`__main__`) redirects it: generation.next_work loads this file on the host to ask
# refusal(), which needs neither the engine nor a redirected stdout.
PROTOCOL = sys.stdout
if __name__ == "__main__":
    sys.stdout = sys.stderr

try:
    import z3  # noqa: E402
    from idp_engine import IDP, Theory  # noqa: E402
except ImportError:
    if __name__ == "__main__":
        raise
    z3 = IDP = Theory = None
# After the redirect above: the engine captures sys.stdout when it is first imported, and the converter imports it.
sys.path.insert(0, str(Path(__file__).resolve().parent))  # dcp_convert_idp.py sits beside this file
# the binding is in dcp_convert_idp.py; generation.brief and next_work import refusal() from here, on the host
from dcp_convert_idp import INT_SET, Unsupported, bind, refusal, sized, vocabulary  # noqa: E402,F401
STARTED = time.monotonic()  # the runner's own clock (benchmarking): read_seconds and main_seconds count from here

# Seconds from loading the submission until its theory and data are handed to Z3,
# and from STARTED until the request was read, for benchmarking.
BUILD_SECONDS = 0.0
READ_SECONDS = 0.0


def emit(record):
    print(json.dumps(record, allow_nan=False), file=PROTOCOL, flush=True)


def finish(status, detail="", **metadata):
    emit({"type": "status", "status": status, "detail": detail, "build_seconds": BUILD_SECONDS,
          "read_seconds": READ_SECONDS, "main_seconds": time.monotonic() - STARTED, **metadata})

INPUT = Path("/input")
DIRECTIONS = ("minimize", "maximize")








































def domain_tests(theory, vocab, name):
    """For an output declared `(domain: p)`, a function from argument tuple to the ground
    atoms that must hold for the tuple to be part of the output; None for a total output."""
    decl = vocab.symbol_decls[name]
    domains, sorts = [str(domain) for domain in decl.domains], [str(sort) for sort in decl.sorts]
    if domains == sorts:
        return None
    if len(domains) == len(sorts):
        atoms = [None if domain == sort else output_terms(theory, domain)
                 for domain, sort in zip(domains, sorts)]
        return lambda index: [atom[(item,)] for atom, item in zip(atoms, index) if atom is not None]
    atoms = output_terms(theory, domains[0])
    return lambda index: [atoms[index]]


def objective(vocab):
    found = [(name, vocab.symbol_decls[name]) for name in DIRECTIONS if name in vocab.symbol_decls]
    if not found:
        return None
    if len(found) > 1:
        raise ValueError("Declare either minimize or maximize, not both")
    name, decl = found[0]
    codomain = str(decl.codomain)
    numeric = codomain == INT_SET or str(getattr(vocab.symbol_decls.get(codomain), "super_set", "")) == INT_SET
    if decl.sorts or not numeric:
        raise ValueError(f"{name} must be a nullary integer function: {name}: () -> Int")
    return name


def literal_argument(name, argument, theory):
    """The Python value of a ground sentence's argument, reduced through the model's
    interpretation when the engine has not already simplified it to a literal."""
    value = getattr(argument, "py_value", None)
    if value is not None:
        return value
    try:
        reduced = z3.simplify(argument.translate(theory))
    except Exception as error:
        raise ValueError(f"Declared output {name} has an argument {argument} that cannot be "
                         f"read from the model: {error}")
    if z3.is_int_value(reduced):
        return reduced.as_long()
    if z3.is_true(reduced) or z3.is_false(reduced):
        return z3.is_true(reduced)
    raise ValueError(f"Declared output {name} has a ground sentence whose argument {argument} "
                     "does not reduce to a value in the model")


def output_terms(theory, name):
    """The ground terms of declared output `name`, keyed by argument tuple."""
    terms = {}
    for assignment in theory.assignments.values():
        sentence = assignment.sentence
        if type(sentence).__name__ == "AppliedSymbol" and sentence.decl.name == name:
            arguments = tuple(literal_argument(name, argument, theory) for argument in sentence.sub_exprs)
            try:
                terms[arguments] = sentence.translate(theory)
            except Exception as error:
                raise ValueError(f"Declared output {name} has a ground sentence that cannot be "
                                 f"translated: {error}")
    if not terms:
        raise ValueError(f"Declared output {name} is not a symbol of the vocabulary")
    return terms


def nest(values):
    """{(i, j): v} with a rectangular index set -> nested lists in ascending order."""
    if not values:
        return []
    arity = len(next(iter(values)))
    if arity == 0:
        return values[()]
    axes = [sorted({index[axis] for index in values}) for axis in range(arity)]

    def build(prefix, axis):
        if axis == arity:
            return values[prefix]
        return [build(prefix + (item,), axis + 1) for item in axes[axis]]
    expected = 1
    for axis in axes:
        expected *= len(axis)
    if expected != len(values):
        raise ValueError("A declared output must be total over its argument types")
    return build((), 0)


def python(value):
    if z3.is_true(value):
        return True
    if z3.is_false(value):
        return False
    if z3.is_int_value(value):
        return value.as_long()
    raise ValueError(f"Declared outputs must be integer or Boolean, got {value}")


def remaining_ms(deadline):
    left = deadline - time.monotonic()
    return None if left <= 0 else max(1, int(left * 1000))


def check(solver, deadline):
    budget = remaining_ms(deadline)
    if budget is None:
        return None
    solver.set("timeout", budget)
    return solver.check()


def incumbents(target, goal, started):
    """A z3 `set_on_model` callback: each strictly better model the optimiser reports while it searches is
    emitted as an incumbent record, with the seconds since `started` (the end of the build)."""
    last = []

    def improved(model):
        value = model.eval(target, model_completion=True)
        if not z3.is_int_value(value):
            return
        value = value.as_long()
        if last and not (value < last[-1] if goal == "minimize" else value > last[-1]):
            return
        last.append(value)
        emit({"type": "incumbent", "objective": value, "seconds": time.monotonic() - started})

    def proven(value):
        """z3 does not hand over every last model: the proven optimum ends the incumbents."""
        if not last or last[-1] != value:
            last.append(value)
            emit({"type": "incumbent", "objective": value, "seconds": time.monotonic() - started})
    improved.proven = proven
    return improved


def load(request):
    source = (INPUT / "model.idp").read_text()
    instance = request["instance"]
    with contextlib.redirect_stdout(sys.stderr):
        idp = IDP.from_str(source)
        full = IDP.from_str(source + "\n" + sized(idp, source, bind(idp, instance)))
        _, vocab = vocabulary(full)
        theory = Theory(*full.theories.values(), *full.structures.values())
    return theory, vocab, objective(vocab)


def solve(request):
    global BUILD_SECONDS
    deadline = time.monotonic() + request["execution_timeout"]
    building = time.monotonic()
    theory, vocab, goal = load(request)
    outputs = {name: output_terms(theory, name) for name in request["outputs"]}
    domains = {name: domain_tests(theory, vocab, name) for name in request["outputs"]}
    solver = theory.solver
    solver.push()
    theory._add_assignment(solver)
    BUILD_SECONDS = time.monotonic() - building

    if goal is not None:
        target = output_terms(theory, goal)[()]
        optimizer = theory.optimize_solver
        optimizer.push()
        theory._add_assignment(optimizer)
        handle = (optimizer.minimize if goal == "minimize" else optimizer.maximize)(target)
        BUILD_SECONDS = time.monotonic() - building
        reporter = incumbents(target, goal, time.monotonic())
        optimizer.set_on_model(reporter)
        status = check(optimizer, deadline)
        if status == z3.unsat:
            return finish("unsat")
        if status != z3.sat:
            return finish("timeout", "Candidate optimum was not proven")
        # For an unbounded objective z3 still answers sat, and model().eval gives
        # the witness model's value rather than the bound; only lower == upper,
        # both finite, is a proven optimum.
        low, high = optimizer.lower(handle), optimizer.upper(handle)
        optimizer.pop()
        if not (z3.is_int_value(low) and z3.is_int_value(high)):
            return finish("error", f"The objective is unbounded: between {low} and {high}")
        if low.as_long() != high.as_long():
            return finish("timeout", "Candidate optimum was not proven")
        best = low
        reporter.proven(best.as_long())
        # Enumerate only assignments achieving the proven optimum.
        solver.add(target == best)

    count = 0
    while count < request["solution_limit"]:
        status = check(solver, deadline)
        if status == z3.unsat:
            return finish("complete" if count else "unsat")
        if status != z3.sat:
            return finish("timeout")
        model = solver.model()

        def holds(atom):
            return z3.is_true(model.eval(atom, model_completion=True))
        shown = {name: {index: term for index, term in terms_.items()
                        if domains[name] is None or all(map(holds, domains[name](index)))}
                 for name, terms_ in outputs.items()}
        values = {name: nest({index: python(model.eval(term, model_completion=True))
                              for index, term in terms_.items()})
                  for name, terms_ in shown.items()}
        terms = [term for terms_ in shown.values() for term in terms_.values()]
        record = {"type": "solution", "values": values}
        if goal is not None:
            # The objective symbol's value on this solution: the problem's own, as the theory defines it.
            record["objective"] = python(model.eval(target, model_completion=True))
        emit(record)
        count += 1
        if count == request["solution_limit"]:
            break
        solver.add(z3.Or([term != model.eval(term, model_completion=True) for term in terms]))
    finish("limit")


def main():
    try:
        global READ_SECONDS
        request = json.loads((INPUT / "request.json").read_text())
        READ_SECONDS = time.monotonic() - STARTED
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by idp_z3")

        def expired(signum, frame):
            raise TimeoutError("Runner execution budget exceeded")

        signal.signal(signal.SIGALRM, expired)
        signal.setitimer(signal.ITIMER_REAL, request["execution_timeout"] + 5)
        solve(request)
    except TimeoutError:
        finish("timeout")
    except Unsupported as error:
        finish("unsupported", str(error))
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error).strip().splitlines()[-1] if str(error).strip() else type(error).__name__)


if __name__ == "__main__":
    main()
