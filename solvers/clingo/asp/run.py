"""Runner protocol for the clingo_asp integration. Runs inside the image only.

A submission is an ASP program. ASP takes a logic program rather than an object
you read fields off, so the instance cannot be handed to the model the way the
Python integrations do it: this runner converts the JSON instance into facts and
grounds them alongside the submission. That conversion is the integration's
contract, so it is deliberately simple and total — index positions first, value
last — and the modelling skill documents it with the same words used here.

Plain ASP has no operation that takes a string apart, so every string value, at
any depth, also arrives one character at a time: `name_char(index, ...,
position, "c")`, laid out as if the string were one more list level. These facts
come in addition to `name(index, ..., "string")`, never instead of it.

Declared outputs come back the same way. The request carries the reference's
output names, and each is matched to the predicate of the same name with its
first letter lowered — the same rule the instance fields use, because an ASP
predicate cannot start with a capital. Index positions come first and the value
last, and this runner rebuilds the nested shape the reference expects.
"""
import json
from pathlib import Path
import signal
import sys
import time

sys.path.insert(0, "/opt/runner")
from dcp_convert_asp import CHARACTERS, facts, predicate  # noqa: E402,F401
from runtime import emit  # noqa: E402
from runtime import finish as runtime_finish  # noqa: E402

import clingo  # noqa: E402
import clingo.ast  # noqa: E402
STARTED = time.monotonic()  # the runner's own clock (benchmarking): read_seconds and main_seconds count from here

INPUT = Path("/input")

# Seconds spent building the model (the instance facts and the program, added and
# grounded), and from STARTED until the request was read, for benchmarking.
BUILD_SECONDS = 0.0
READ_SECONDS = 0.0


def finish(status, detail="", **metadata):
    runtime_finish(status, detail, build_seconds=BUILD_SECONDS, read_seconds=READ_SECONDS,
                   main_seconds=time.monotonic() - STARTED, **metadata)




def value_of(symbol):
    if symbol.type == clingo.SymbolType.Number:
        return symbol.number
    text = str(symbol)
    if text in ("true", "false"):
        return text == "true"
    raise ValueError(f"Declared outputs must be integers or true/false; got {text}")


def nest(entries, name):
    """Rebuild a nested list from (index tuple, value) pairs."""
    if not entries[0][0]:
        if len(entries) != 1:
            raise ValueError(f"Output {name} has several values but no index")
        return entries[0][1]
    groups = {}
    for indices, value in entries:
        groups.setdefault(indices[0], []).append((indices[1:], value))
    order = sorted(groups)
    if order != list(range(len(order))):
        raise ValueError(f"Output {name} indices must be 0-based and contiguous, got {order}")
    return [nest(groups[position], name) for position in order]


def declared_names(outputs):
    """Map each declared output key to the predicate that carries it.

    An ASP predicate cannot start with a capital, so a key like `A` is carried by
    the predicate `a` and `_A` by `_a`, exactly as instance fields are lowered on
    the way in.
    """
    wanted = {}
    for key in outputs or []:
        name = predicate(key)
        if name in wanted:
            raise ValueError(f"Declared outputs {wanted[name]!r} and {key!r} collide as {name!r}")
        wanted[name] = key
    return wanted


def outputs_of(model, wanted):
    collected = {name: [] for name in wanted}
    for symbol in model.symbols(shown=True):
        if symbol.name in collected:
            arguments = symbol.arguments
            collected[symbol.name].append(
                (tuple(a.number for a in arguments[:-1]), value_of(arguments[-1])))
    result = {}
    for name, entries in collected.items():
        key = wanted[name]
        if not entries:
            raise ValueError(f"The program shows no {name}/N atoms for declared output {key!r}")
        width = len(entries[0][0])
        if any(len(indices) != width for indices, _ in entries):
            raise ValueError(f"Output {key!r} mixes arities")
        result[key] = nest(entries, key)
    return result


def objective_sign(program):
    """How a one-level cost reads as the program's objective value: 1 when every optimisation statement is a
    `#minimize` (or weak constraint), -1 when every one is a `#maximize`, None when they mix or cannot be told.

    clingo stores `#maximize { w }` as the cost -w, and its syntax tree is the same as `#minimize { -w }`'s, so
    the program is parsed twice, once with `#maximize`/`#maximise` spelled `#minimize`: a statement that
    changes came from a `#maximize`. Only for the objectives the runner reports; the search never sees this.
    """
    def statements(text):
        found = []
        clingo.ast.parse_string(text, lambda s: found.append(str(s))
                                if s.ast_type == clingo.ast.ASTType.Minimize else None)
        return found
    try:
        plain = statements(program)
        renamed = statements(program.replace("#maximize", "#minimize").replace("#maximise", "#minimize"))
    except Exception:
        return None
    if not plain or len(plain) != len(renamed):
        return None
    changed = [a != b for a, b in zip(plain, renamed)]
    return -1 if all(changed) else (None if any(changed) else 1)


def solve(request):
    global BUILD_SECONDS
    deadline = time.monotonic() + request["execution_timeout"]
    program = (INPUT / "model.lp").read_text(encoding="utf-8")
    sign = objective_sign(program)
    building = time.monotonic()
    control = clingo.Control(["0"])
    control.configuration.solve.opt_mode = "optN"
    control.add("base", [], facts(request["instance"]) + "\n" + program)
    control.ground([("base", [])])
    BUILD_SECONDS = time.monotonic() - building
    search_start = time.monotonic()
    best = None  # the lowest one-level cost reported as an incumbent so far

    wanted = declared_names(request.get("outputs"))
    seen, count, optimizing = set(), 0, False
    with control.solve(yield_=True, async_=True) as handle:
        while count < request["solution_limit"]:
            left = deadline - time.monotonic()
            if left <= 0 or not handle.wait(left):
                handle.cancel()
                # An optimization program that never proved its optimum has not
                # answered the question, so it must not look like success.
                return finish("timeout")
            model = handle.model()
            if model is None:
                # Exhausted. For an optimization program that is only a real
                # answer once some model was proven optimal.
                return finish("complete" if count else ("timeout" if optimizing else "unsat"))
            optimizing = optimizing or bool(model.cost)
            # The problem has one integer objective, which the runner reports on every solution: the program's
            # own sum, read from a one-level cost with a known direction. Anything else has no such value.
            if model.cost and (sign is None or len(model.cost) != 1):
                handle.cancel()
                return finish("error", "The objective must be one priority level stated with #minimize (or weak "
                                       "constraints) only or #maximize only, so that its value is the problem's "
                                       f"objective; clingo reports the cost {list(model.cost)}")
            # Each strictly better model of the optimisation phase is an incumbent.
            if model.cost and (best is None or model.cost[0] < best):
                best = model.cost[0]
                emit({"type": "incumbent", "objective": sign * best,
                      "seconds": time.monotonic() - search_start})
            if model.cost and not model.optimality_proven:
                handle.resume()
                continue
            values = outputs_of(model, wanted)
            key = json.dumps(values, sort_keys=True)
            if key not in seen:
                seen.add(key)
                record = {"type": "solution", "values": values}
                if model.cost:
                    # clingo minimises: a #maximize's sum is the negated cost.
                    record["objective"] = sign * model.cost[0]
                emit(record)
                count += 1
            handle.resume()
    finish("limit")


def main():
    try:
        global READ_SECONDS
        request = json.loads((INPUT / "request.json").read_text())
        READ_SECONDS = time.monotonic() - STARTED
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by clingo_asp")

        def expired(signum, frame):
            raise TimeoutError("Runner execution budget exceeded")

        signal.signal(signal.SIGALRM, expired)
        signal.setitimer(signal.ITIMER_REAL, request["execution_timeout"] + 5)
        solve(request)
    except TimeoutError:
        finish("timeout")
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))


if __name__ == "__main__":
    main()
