# car_selection: a CPMpy model from DCP Rosetta.
# Download the `car_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python car_selection.py car_selection.json

import cpmpy as cp


def create_model(instance):
    """Assign participants to cars to maximise the number of assignments: each participant is
    interested in a subset of the cars, gets at most one car, and each car goes to at most one
    participant."""
    # possible_assignments[i][j]: 1 when participant i is interested in car j, otherwise 0
    possible = cp.cpm_array(instance["possible_assignments"])
    participants, cars = possible.shape

    # assignments[i, j] is true when participant i is assigned to car j
    assignments = cp.boolvar(shape=(participants, cars), name="assignments")

    model = cp.Model()
    # A participant can only be assigned a car they are interested in.
    model.add(assignments <= possible)
    # Each participant is assigned at most one car.
    model.add(assignments.sum(axis=1) <= 1)
    # Each car is assigned to at most one participant.
    model.add(assignments.sum(axis=0) <= 1)

    # Maximise the number of assignments.
    model.maximize(cp.sum(assignments))

    return model, {"assignments": assignments}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
