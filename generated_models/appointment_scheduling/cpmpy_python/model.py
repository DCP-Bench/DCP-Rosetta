# appointment_scheduling: a CPMpy model from DCP Rosetta.
# Download the `appointment_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python appointment_scheduling.py appointment_scheduling.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Schedule people into interview slots based on their free-busy schedules:
    every person gets exactly one slot in which they are free, and every slot
    gets exactly one person."""
    free = np.array(instance["m"])  # free[i][j] is 1 when person i is free in slot j, else 0
    n = len(free)  # the number of people, which is also the number of slots

    # x[i, j] is true when person i is assigned to slot j
    x = cp.boolvar(shape=(n, n), name="x")

    model = cp.Model()

    # Each person is assigned to exactly one slot, and is free in it.
    model.add((x * free).sum(axis=1) == 1)
    model.add(x.sum(axis=1) == 1)
    # Each slot gets exactly one person.
    model.add(x.sum(axis=0) == 1)

    return model, {"x": x}


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
