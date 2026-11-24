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


def reporting_incumbents(solve_instance):
    """The optimising solve (runtime.py's only Instance.solve) streams its solutions instead, with
    `intermediate_solutions=True`, which only makes Gecode print each improving solution it finds on its
    branch-and-bound search (the search is unchanged): each is emitted as an incumbent with its objective
    (`Result.objective`, the `objective` variable, the problem's own value) as it arrives, strictly improving,
    and the last solution (the optimum, once the status says so) is returned as `solve` would return it.
    `seconds` is MiniZinc's own solution time (`time`, from the start of the minizinc process) less its
    flattening time (`flatTime`), so it counts from the start of the search, after the model is built; where
    MiniZinc gives no such time it counts from this call. Incumbents carry no values."""
    def wrapped(instance, *args, **kwargs):
        import asyncio
        import time
        import minizinc
        if (instance.method == minizinc.Method.SATISFY or kwargs.get("intermediate_solutions") is not False
                or Optimum.value is not None):
            return solve_instance(instance, *args, **kwargs)
        started = time.monotonic()
        kwargs = {**kwargs, "intermediate_solutions": True}

        async def streamed():
            status, solution, statistics = minizinc.Status.UNKNOWN, None, {}
            flattening, last, seconds = None, None, 0.0
            async for result in instance.solutions(*args, **kwargs):
                status = result.status
                statistics.update(result.statistics)
                if flattening is None and "flatTime" in result.statistics:
                    flattening = result.statistics["flatTime"].total_seconds()
                if result.solution is None:
                    continue
                solution = result.solution
                value = result.objective
                if isinstance(value, bool) or value is None or int(value) != value:
                    raise ValueError("Use an integer objective")
                value = int(value)
                if last is not None and not (value < last if instance.method == minizinc.Method.MINIMIZE
                                             else value > last):
                    continue
                at = result.statistics.get("time")
                found = (at.total_seconds() - (flattening or 0.0) if at is not None
                         else time.monotonic() - started)
                seconds = max(seconds, found, 0.0)
                runtime.emit({"type": "incumbent", "objective": value, "seconds": seconds})
                last = value
            return minizinc.Result(status, solution, statistics)

        return asyncio.run(streamed())
    return wrapped


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
    minizinc.Instance.solve = remembering_objective(reporting_incumbents(minizinc.Instance.solve))
    runtime.emit = with_objective(runtime.emit)
    runtime.main("minizinc")
