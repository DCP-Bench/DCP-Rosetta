import contextlib
import importlib.util
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
    objective = model.proto.objective
    terms = sum(c * solver.value(model.get_int_var_from_proto_index(i))
                for i, c in zip(objective.vars, objective.coeffs))
    scaling = objective.scaling_factor or 1
    if scaling != int(scaling) or objective.offset != int(objective.offset):
        raise ValueError("Use an integer objective")
    return int(scaling) * (terms + int(objective.offset))


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
    cp_model.CpSolver.solve = remembering_objective(cp_model.CpSolver.solve)
    runtime.emit = with_objective(runtime.emit)
    runtime.main("cp_sat")
