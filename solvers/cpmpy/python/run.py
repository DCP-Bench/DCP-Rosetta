import contextlib
import importlib.util
import json
import sys
import time
sys.path.insert(0, "/opt/runner")
import runtime

STDOUT = sys.stdout  # runtime.py solves with stdout redirected to stderr; incumbents still go to the protocol stream


def build(request):
    """runtime.build, with the entrypoint named create_model(instance). Models retained
    before the rename define build(instance), which is still accepted. The file is
    loaded as module "candidate", so its `if __name__ == "__main__":` block never runs."""
    spec = importlib.util.spec_from_file_location("candidate", "/input/model.py")
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        create_model = getattr(module, "create_model", None) or module.build
        model, outputs = create_model(request["instance"])
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("create_model(instance) must return (model, nonempty output-expression dictionary)")
    Search.outputs = outputs
    return model, outputs


def solve_without_guard_when_no_objective(solve):
    """runtime.py passes keep_all_feasible_solutions_in_presolve=True on every solve.
    Only an objective needs it (https://github.com/google/or-tools/issues/5552); the
    enumeration solves have none, and with the guard handshaking's second solve takes
    over 180 s instead of 0.8 s.
    Move this into runtime.py when that file next changes."""
    def wrapped(model, *args, **kwargs):
        if not model.has_objective():
            kwargs.pop("keep_all_feasible_solutions_in_presolve", None)
        return solve(model, *args, **kwargs)
    return wrapped


class Optimum:
    """The objective value of the proven optimum, in the problem's own terms: CPMpy evaluates the model's
    objective expression on the solution (`Model.objective_value()`), constants and direction included.
    runtime.py emits solution records without it; with_objective adds it to each one. Every solution of an
    optimisation is at the optimum: runtime.py enumerates further ones with the objective fixed to it.
    Move this into runtime.py when that file next changes."""
    value = None


class Search:
    """What the incumbents need: the request (does it ask for values?) and the declared outputs."""
    request = {}
    outputs = None


def read(e):
    """One declared output value, as runtime.python_solver reads it for the solution record."""
    import numbers
    import numpy as np
    value = e.value() if hasattr(e, "value") else e
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if not isinstance(value, numbers.Integral):
        raise ValueError("Declared outputs must be integer or Boolean values; no coercion from floats/strings")
    return int(value)


def reporting_incumbents(solve):
    """The first, optimising solve reports each improving solution CP-SAT finds as an incumbent: a CP-SAT
    solution callback gives its values to the CPMpy variables (as cpmpy.solvers.ortools.OrtSolutionPrinter
    does, through the solver's variable map), then the objective is the model's objective expression evaluated
    there, in the problem's own terms, and `values` (only when the request says incumbent_values) the declared
    outputs read as for the solution record. `seconds` counts from the start of this solve, after the build.
    The enumeration solves runtime.py makes afterwards have no objective and report none."""
    def wrapped(model, *args, solver=None, time_limit=None, **kwargs):
        if solver != "ortools" or not model.has_objective() or Optimum.value is not None:
            return solve(model, *args, solver=solver, time_limit=time_limit, **kwargs)
        from cpmpy.solvers.solver_interface import ExitStatus
        from cpmpy.solvers.utils import SolverLookup
        from cpmpy.transformations.get_variables import get_variables
        from ortools.sat.python import cp_model
        started = time.monotonic()
        with_values = bool(Search.request.get("incumbent_values"))
        objective = model.objective_
        last = []

        def report(value):
            record = {"type": "incumbent", "objective": value, "seconds": time.monotonic() - started}
            if with_values:
                record["values"] = runtime.mapped(Search.outputs, read)
            print(json.dumps(record, allow_nan=False), file=STDOUT, flush=True)
            last.append(value)

        s = SolverLookup.get("ortools", model)
        # Values for the objective's variables, and for the outputs' only when they are reported.
        shown = get_variables([objective] + (runtime.flatten(Search.outputs) if with_values else []))

        failed = []

        class Incumbents(cp_model.CpSolverSolutionCallback):
            def on_solution_callback(self):
                try:
                    for variable in shown:
                        value = self.Value(s._varmap[variable.name])
                        variable._value = bool(value) if variable.is_bool() else value
                    value = int(objective.value())
                    if not last or (value < last[-1] if model.objective_is_min else value > last[-1]):
                        report(value)
                except Exception as error:  # raised after the solve, as runtime.main reports any failure
                    failed.append(error)
                    self.StopSearch()

        ok = s.solve(time_limit=time_limit, solution_callback=Incumbents(), **kwargs)
        model.cpm_status = s.status()  # as cpmpy.Model.solve does
        if failed:
            raise failed[0]
        if ok and model.status().exitstatus == ExitStatus.OPTIMAL:
            # s.solve has given the optimum's values to the variables; the incumbents end at the optimum.
            value = int(model.objective_value())
            if not last or last[-1] != value:
                report(value)
        return ok
    return wrapped


def remembering_objective(solve):
    def wrapped(model, *args, **kwargs):
        ok = solve(model, *args, **kwargs)
        if ok and model.has_objective():
            Optimum.value = int(model.objective_value())
        return ok
    return wrapped


def with_objective(emit):
    def wrapped(record):
        if record.get("type") == "solution" and Optimum.value is not None:
            record = {**record, "objective": Optimum.value}
        return emit(record)
    return wrapped


def remembering_request(python_solver):
    def wrapped(kind, request):
        Search.request = request
        return python_solver(kind, request)
    return wrapped


runtime.build = build
runtime.python_solver = remembering_request(runtime.python_solver)

if __name__ == "__main__":
    import cpmpy
    cpmpy.Model.solve = remembering_objective(reporting_incumbents(solve_without_guard_when_no_objective(cpmpy.Model.solve)))
    runtime.emit = with_objective(runtime.emit)
    runtime.main("cpmpy")
