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


runtime.build = build

if __name__ == "__main__":
    import cpmpy
    cpmpy.Model.solve = remembering_objective(solve_without_guard_when_no_objective(cpmpy.Model.solve))
    runtime.emit = with_objective(runtime.emit)
    runtime.main("cpmpy")
