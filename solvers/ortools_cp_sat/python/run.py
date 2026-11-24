import contextlib
import importlib.util
import time
import sys
sys.path.insert(0, "/opt/runner")
import runtime


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
    return model, outputs


class Optimum:
    """The objective value of the proven optimum, in the problem's own terms. CP-SAT keeps an objective as
    integer terms plus an offset and a scaling factor (-1 for a maximisation, whose terms and offset it
    negates), so the value is scaling_factor * (terms + offset), computed exactly from the solution's values
    rather than read from the floating-point `objective_value`. runtime.py emits solution records without it;
    with_objective adds it to each one. Every solution of an optimisation is at the optimum: runtime.py
    enumerates further ones with the objective fixed to it. Move this into runtime.py when that file next changes."""
    value = None


def objective_value(solver, model):
    """solver is a CpSolver after the solve, or a CpSolverSolutionCallback during it: both have value()."""
    objective = model.proto.objective
    terms = sum(c * solver.value(model.get_int_var_from_proto_index(i))
                for i, c in zip(objective.vars, objective.coeffs))
    scaling = objective.scaling_factor or 1
    if scaling != int(scaling) or objective.offset != int(objective.offset):
        raise ValueError("Use an integer objective")
    return int(scaling) * (terms + int(objective.offset))


def reporting_incumbents(solve):
    """The first, optimising solve reports each improving solution CP-SAT finds as an incumbent, from a
    solution callback: its objective is objective_value on the callback's solution (the problem's own value,
    as for the solution records). Incumbents carry no values. `seconds` counts
    from the start of this solve, after the build. The enumeration solves runtime.py makes afterwards have
    no objective (it is cleared and pinned) and report none."""
    def wrapped(solver, model, solution_callback=None, *args, **kwargs):
        from ortools.sat.python import cp_model
        if solution_callback is not None or not model.has_objective() or Optimum.value is not None:
            return solve(solver, model, solution_callback, *args, **kwargs)
        started = time.monotonic()
        minimize = (model.proto.objective.scaling_factor or 1) > 0
        last = []
        failed = []

        def report(value):
            runtime.emit({"type": "incumbent", "objective": value, "seconds": time.monotonic() - started})
            last.append(value)

        class Incumbents(cp_model.CpSolverSolutionCallback):
            def on_solution_callback(self):
                try:
                    value = objective_value(self, model)
                    if not last or (value < last[-1] if minimize else value > last[-1]):
                        report(value)
                except Exception as error:  # raised after the solve, as runtime.main reports any failure
                    failed.append(error)
                    self.stop_search()

        status = solve(solver, model, Incumbents(), *args, **kwargs)
        if failed:
            raise failed[0]
        if status == cp_model.OPTIMAL:
            # The incumbents end at the proven optimum, read from the solver's final solution.
            value = objective_value(solver, model)
            if not last or last[-1] != value:
                report(value)
        return status
    return wrapped


def remembering_objective(solve):
    def wrapped(solver, model, *args, **kwargs):
        from ortools.sat.python import cp_model
        status = solve(solver, model, *args, **kwargs)
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) and model.has_objective():
            Optimum.value = objective_value(solver, model)
        return status
    return wrapped


def with_objective(emit):
    def wrapped(record):
        if record.get("type") == "solution" and Optimum.value is not None:
            record = {**record, "objective": Optimum.value}
        return emit(record)
    return wrapped


runtime.build = build

if __name__ == "__main__":
    from ortools.sat.python import cp_model
    cp_model.CpSolver.solve = remembering_objective(reporting_incumbents(cp_model.CpSolver.solve))
    runtime.emit = with_objective(runtime.emit)
    runtime.main("cp_sat")
