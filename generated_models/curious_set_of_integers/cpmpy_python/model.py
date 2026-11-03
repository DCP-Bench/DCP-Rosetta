# curious_set_of_integers: a CPMpy model from DCP Rosetta.
# Download the `curious_set_of_integers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python curious_set_of_integers.py curious_set_of_integers.json

import cpmpy as cp


def create_model(instance):
    """The integers 1, 3, 8 and 120 form a set in which the product of any two
    integers is one less than a perfect square. Find a fifth number (at least 0)
    that can be added to the set without destroying this property."""
    n = instance["n"]              # the number of integers in the extended set
    max_val = instance["max_val"]  # the largest value an integer may take

    # x[i] is the i-th integer of the set; the last one is the number to find
    x = cp.intvar(0, max_val, shape=n, name="x")

    model = cp.Model()
    # The set contains the integers 1, 3, 8 and 120 of the problem statement,
    # and all its integers differ.
    model.add(x[:4] == [1, 3, 8, 120])
    model.add(cp.AllDifferent(x))

    # The product of any two integers is one less than a perfect square.
    for i in range(n):
        for j in range(i + 1, n):
            # root is the square root of x[i] * x[j] + 1; it cannot exceed max_val
            root = cp.intvar(0, max_val, name=f"root_{i}_{j}")
            model.add(root * root == x[i] * x[j] + 1)

    return model, {"number": x[-1]}


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
