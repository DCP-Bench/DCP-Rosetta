# appointment_scheduling: a hermax (Python) model from DCP Rosetta.
# Download the `appointment_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
# Then run it on the first instance (after `pip install hermax`):
#   python appointment_scheduling.py appointment_scheduling.json

from hermax.model import Model


def create_model(instance):
    """Schedule n people into n interview slots: every person gets exactly one slot,
    every slot goes to exactly one person, and each person is only given a slot in
    which they are free. Satisfaction problem, no objective."""
    free = instance["m"]  # free[i][j] = 1 if person i is free in slot j, 0 if busy
    n = len(free)         # the number of people, which equals the number of slots

    m = Model()

    # x[i][j] is true when person i is assigned to interview slot j
    x = m.bool_matrix("x", n, n)

    # Each person is interviewed in exactly one slot.
    for i in range(n):
        m &= x.row(i).exactly_one()

    # Each slot is given to exactly one person.
    for j in range(n):
        m &= x.col(j).exactly_one()

    # A person may only be placed in a slot where they are free.
    for i in range(n):
        for j in range(n):
            if free[i][j] == 0:
                m &= ~x[i][j]

    return m, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
