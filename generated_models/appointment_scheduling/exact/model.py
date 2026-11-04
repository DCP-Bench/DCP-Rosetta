# appointment_scheduling: an Exact (Python) model from DCP Rosetta.
# Download the `appointment_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python appointment_scheduling.py appointment_scheduling.json

from exact import Exact


def create_model(instance):
    """Give each of n people one of n interview slots, one person per slot,
    so that every person gets a slot in which they are free."""
    free = instance["m"]  # free[i][j] is 1 when person i is free in slot j, and 0 when busy
    n_people = len(free)  # as many slots as people

    solver = Exact()

    # Exact identifies its variables by name.
    # x[i][j] is true when person i is given interview slot j
    x = [[f"x_{i}_{j}" for j in range(n_people)] for i in range(n_people)]
    for i in range(n_people):
        for j in range(n_people):
            solver.addVariable(x[i][j], 0, 1)

    # Each person is given a slot in which they are free.
    for i in range(n_people):
        free_slots = [(free[i][j], x[i][j]) for j in range(n_people) if free[i][j]]
        solver.addConstraint(free_slots, True, 1, True, 1)

    # Each person is given exactly one slot.
    for i in range(n_people):
        solver.addConstraint([(1, x[i][j]) for j in range(n_people)], True, 1, True, 1)

    # Each slot is given to exactly one person.
    for j in range(n_people):
        solver.addConstraint([(1, x[i][j]) for i in range(n_people)], True, 1, True, 1)

    return solver, {"x": x}


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
