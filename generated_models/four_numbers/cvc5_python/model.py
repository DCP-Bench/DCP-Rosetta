# four_numbers: a cvc5 (Python) model from DCP Rosetta.
# Download the `four_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_numbers.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python four_numbers.py four_numbers.json

import itertools

import cvc5.pythonic as c5


def create_model(instance):
    """Given up to four distinct integers between 1 and 10, find three integers between 1 and 10
    such that every given number is the sum of some of the three. Print the three integers (x)."""
    numbers = instance["numbers"]  # the numbers to make, up to four, each from 1 to 10

    # The three integers to find.
    x = c5.Ints(["x0", "x1", "x2"])

    # Each integer is from 1 to 10.
    bounds = [v >= 1 for v in x] + [v <= 10 for v in x]

    # The sum of one, two or all three of the integers.
    subsets = [c5.Sum([x[j] for j in group])
               for size in range(1, 4) for group in itertools.combinations(range(3), size)]

    solver = c5.Solver()

    # Each given number is one of these sums.
    solver.add(bounds + [c5.Or([s == v for s in subsets]) for v in numbers])

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
