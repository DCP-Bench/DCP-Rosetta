# car_selection: a PyCSP3 model from DCP Rosetta.
# Download the `car_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python car_selection.py car_selection.json

from pycsp3 import *


def create_model(instance):
    """Assign participants to cars so as to maximise the total number of assignments.
    Each participant may be interested in a subset of the cars. Each participant is
    assigned to at most one car, and each car to at most one participant."""
    interested = instance["possible_assignments"]  # interested[p][c] = 1 if participant p is interested in car c
    n_participants = len(interested)
    n_cars = len(interested[0])

    # assignments[p][c] is 1 when participant p is assigned to car c
    assignments = VarArray(size=[n_participants, n_cars], dom={0, 1})

    satisfy(
        # Each participant is assigned to at most one car.
        [Sum(assignments[p]) <= 1 for p in range(n_participants)],
        # Each car is assigned to at most one participant.
        [Sum(assignments[:, c]) <= 1 for c in range(n_cars)],
        # A participant is only assigned to a car they are interested in.
        [assignments[p][c] <= interested[p][c] for p in range(n_participants) for c in range(n_cars)],
    )

    # Maximise the total number of assignments.
    maximize(Sum(assignments))

    return {"assignments": assignments}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("assignments", "=")
        for row in outputs["assignments"]:
            print(values(row))
    else:
        print("No solution:", status())
