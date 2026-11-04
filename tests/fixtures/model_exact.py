from exact import Exact


def create_model(instance):
    n = instance["n"]
    solver = Exact()
    solver.addVariable("x", 0, n)
    solver.addVariable("y", 0, n)
    if not instance["optimize"]:
        solver.addConstraint([(1, "x"), (1, "y")], True, n, True, n)
        return solver, {"x": "x", "y": "y"}
    solver.addConstraint([(1, "x"), (1, "y")], True, n)
    solver.setObjective([(1, "x"), (1, "y")], minimize=True)
    return solver, {"x": "x", "y": "y"}
