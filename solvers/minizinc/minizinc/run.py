"""MiniZinc on Gecode, with the instance binding this integration adds.

The binding itself, which turns each JSON instance field into something MiniZinc's data interface accepts, is in
dcp_convert_mzn.py (its docstring has the rules). It is a separate file because readers download it to prepare
their own data; the evaluator imports it, so both bind identically. A refusal is an `error` status with the
reason as detail, exactly as any other failure in `runtime.main`, because the binding runs inside it.
"""
import sys
from pathlib import Path
sys.path.insert(0, "/opt/runner")
sys.path.insert(0, str(Path(__file__).resolve().parent))  # dcp_convert_mzn.py sits beside this file
import runtime
from dcp_convert_mzn import bind, refusal  # noqa: F401  (generation.brief and next_work import refusal() from here)

# The generation tools load this file on the host with an empty `runtime`, only for refusal().
solve = getattr(runtime, "minizinc_solver", None)


class Optimum:
    """The objective value of the proven optimum, in the problem's own terms: MiniZinc reports the value of
    the solve item's expression (`_objective`, `Result.objective`), which the contract makes the integer
    `objective` variable, constants and direction included. runtime.py emits solution records without it;
    with_objective adds it to each one. Every solution of an optimisation is at the optimum: runtime.py
    enumerates further ones with `constraint objective = <optimum>`. Move this into runtime.py when that file
    next changes."""
    value = None


def remembering_objective(solve_instance):
    def wrapped(instance, *args, **kwargs):
        import minizinc
        result = solve_instance(instance, *args, **kwargs)
        if result.status == minizinc.Status.OPTIMAL_SOLUTION and result.objective is not None:
            if isinstance(result.objective, bool) or int(result.objective) != result.objective:
                raise ValueError("Use an integer objective")
            Optimum.value = int(result.objective)
        return result
    return wrapped


def with_objective(emit):
    def wrapped(record):
        if record.get("type") == "solution" and Optimum.value is not None:
            record = {**record, "objective": Optimum.value}
        return emit(record)
    return wrapped


def minizinc_solver(request):
    if not request["legacy"]:
        request = {**request, "instance": bind(request["instance"])}
    return solve(request)


# runtime.main dispatches to the module-level minizinc_solver, so replacing it
# keeps main's request parsing, time budget, status and error handling unchanged.
runtime.minizinc_solver = minizinc_solver

if __name__ == "__main__":
    import minizinc
    minizinc.Instance.solve = remembering_objective(minizinc.Instance.solve)
    runtime.emit = with_objective(runtime.emit)
    runtime.main("minizinc")
