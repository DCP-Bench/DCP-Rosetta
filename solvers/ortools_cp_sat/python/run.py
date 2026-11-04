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


runtime.build = build

if __name__ == "__main__":
    runtime.main("cp_sat")
