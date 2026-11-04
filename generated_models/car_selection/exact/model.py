# car_selection: an Exact (Python) model from DCP Rosetta.
# Download the `car_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python car_selection.py car_selection.json

from exact import Exact


def create_model(instance):
    """Assign participants to cars they are interested in. Each participant gets at most one
    car, and each car goes to at most one participant. Make as many assignments as possible."""
    possible = instance["possible_assignments"]  # possible[i][j] is 1 when participant i is interested in car j
    n_participants = len(possible)
    n_cars = len(possible[0])

    solver = Exact()

    # Exact identifies its variables by name.
    # assignments[i][j] is 1 when participant i gets car j, and 0 when not. A participant
    # can only get a car they are interested in.
    assignments = [[f"a{i}_{j}" for j in range(n_cars)] for i in range(n_participants)]
    for i in range(n_participants):
        for j in range(n_cars):
            solver.addVariable(assignments[i][j], 0, possible[i][j])

    # Each participant gets at most one car.
    for i in range(n_participants):
        solver.addConstraint([(1, name) for name in assignments[i]], False, 0, True, 1)

    # Each car goes to at most one participant.
    for j in range(n_cars):
        solver.addConstraint([(1, assignments[i][j]) for i in range(n_participants)],
                             False, 0, True, 1)

    # Every assignment counts once towards the total.
    matched = [(1, name) for row in assignments for name in row]
    solver.setObjective(matched, minimize=False)

    return solver, {"assignments": assignments}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
