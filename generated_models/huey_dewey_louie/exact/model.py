# huey_dewey_louie: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
# Run it (after `pip install exact numpy`) with:
#   python huey_dewey_louie.py

from exact import Exact


def create_model(instance):
    """Huey, Dewey and Louie are cub scouts questioned by their uncle, so they cannot
    lie and each of their statements is true. Who is guilty?"""
    solver = Exact()

    # Exact identifies its variables by name.
    # Whether each nephew is guilty: 1 when guilty, 0 when not.
    for name in ("huey", "dewey", "louie"):
        solver.addVariable(name, 0, 1)

    # Huey: Dewey and Louie have an equal share in it, so one is guilty exactly when the other is.
    solver.addConstraint([(1, "dewey"), (-1, "louie")], True, 0, True, 0)
    # Dewey: if Huey is guilty, then so am I.
    solver.addConstraint([(1, "dewey"), (-1, "huey")], True, 0)
    # Louie: Dewey and I are not both guilty.
    solver.addConstraint([(1, "dewey"), (1, "louie")], False, 0, True, 1)

    return solver, {"huey": "huey", "dewey": "dewey", "louie": "louie"}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
