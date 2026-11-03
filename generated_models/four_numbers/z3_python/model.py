# four_numbers: a Z3 (Python) model from DCP Rosetta.
# Download the `four_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_numbers.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python four_numbers.py four_numbers.json

import z3


def create_model(instance):
    """Given up to four distinct integers between 1 and 10, find three integers between 1 and 10
    such that every given number is the sum of some of the three."""
    numbers = instance["numbers"]  # numbers[i]: the i-th given number
    n_numbers = len(numbers)
    n_found = 3  # how many integers to find

    # x[j] is the j-th of the three integers to find
    x = [z3.Int(f"x_{j}") for j in range(n_found)]
    # use[i][j] is true when x[j] is one of the integers that add up to numbers[i]
    use = [[z3.Bool(f"use_{i}_{j}") for j in range(n_found)] for i in range(n_numbers)]

    solver = z3.Solver()

    # Each integer to find is between 1 and 10.
    solver.add([z3.And(1 <= xj, xj <= 10) for xj in x])

    # Each given number is the sum of the integers chosen for it.
    solver.add([
        z3.Sum([z3.If(use[i][j], x[j], 0) for j in range(n_found)]) == numbers[i]
        for i in range(n_numbers)
    ])

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
