# four_numbers: a CPMpy model from DCP Rosetta.
# Download the `four_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_numbers.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python four_numbers.py four_numbers.json

import cpmpy as cp


def create_model(instance):
    """Given up to four distinct integers between 1 and 10, find three integers
    between 1 and 10 such that every given number is the sum of a subset of them."""
    numbers = instance["numbers"]  # numbers[i]: the i-th number that must be a subset sum
    m = len(numbers)
    n = 3  # the number of integers to find

    # x[j] is the j-th of the three integers to find
    x = cp.intvar(1, 10, shape=n, name="x")
    # uses[i, j] is true when x[j] is part of the subset that sums to numbers[i]
    uses = cp.boolvar(shape=(m, n), name="uses")

    model = cp.Model()
    # Each given number is the sum of the integers in its subset.
    for i in range(m):
        model.add(cp.sum(uses[i] * x) == numbers[i])

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
