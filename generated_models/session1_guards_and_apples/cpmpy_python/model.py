# session1_guards_and_apples: a CPMpy model from DCP Rosetta.
# Download the `session1_guards_and_apples.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python session1_guards_and_apples.py session1_guards_and_apples.json

import cpmpy as cp


def create_model(instance):
    """A boy passes through a number of gates to give an apple to a girl. He
    bribes each guard with half of his apples plus one, always a whole number
    of apples, and has none left after giving the girl her apple."""
    num_gates = instance["num_gates"]  # how many gates (and guards) the boy passes

    # apples[i] is the number of apples the boy has before gate i; the last entry
    # is the number after the last gate. The bound of 100 apples covers the gate
    # counts of the instances (each extra gate roughly doubles the count).
    apples = cp.intvar(0, 100, shape=num_gates + 1, name="apples")

    model = cp.Model()

    # After the last gate the boy has one apple left, which he gives to the girl.
    model.add(apples[num_gates] == 1)

    # At each gate the boy gives half of his apples plus one, so before the gate
    # he had twice what remains afterwards plus 2.
    for i in range(num_gates):
        model.add(apples[i] == 2 * (apples[i + 1] + 1))

    return model, {"apples": apples}


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
