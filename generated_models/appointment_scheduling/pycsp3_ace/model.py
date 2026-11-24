# appointment_scheduling: a PyCSP3 model from DCP Rosetta.
# Download the `appointment_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python appointment_scheduling.py appointment_scheduling.json

from pycsp3 import *


def create_model(instance):
    """Four people are to be scheduled into four interview slots, each in a slot in which
    they are free. Each person gets exactly one slot and each slot goes to exactly one person."""
    m = instance["m"]  # m[i][j] is 1 when person i is free in slot j, else 0
    n_people = len(m)
    n_slots = len(m[0])

    # x[i][j] is 1 when person i is assigned to slot j, else 0
    x = VarArray(size=[n_people, n_slots], dom={0, 1})

    satisfy(
        # Each person gets exactly one slot.
        [Sum(x[i]) == 1 for i in range(n_people)],
        # Each slot goes to exactly one person.
        [Sum(x[:, j]) == 1 for j in range(n_slots)],
        # A person is assigned only a slot in which they are free.
        [x[i][j] <= m[i][j] for i in range(n_people) for j in range(n_slots)],
    )

    return {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("x", "=")
        for row in outputs["x"]:
            print(values(row))
    else:
        print("No solution:", status())
