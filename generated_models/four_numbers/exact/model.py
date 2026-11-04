# four_numbers: an Exact (Python) model from DCP Rosetta.
# Download the `four_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_numbers.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python four_numbers.py four_numbers.json

from exact import Exact


def create_model(instance):
    """Given up to four distinct integers between 1 and 10, find three integers between 1
    and 10 such that every given number is the sum of some of the three."""
    numbers = instance["numbers"]  # numbers[i] must be the sum of some of the three integers
    n_integers = 3  # how many integers to find

    solver = Exact()

    # Exact identifies its variables by name.
    # x[j] is the j-th of the integers to find.
    x = [f"x_{j}" for j in range(n_integers)]
    for name in x:
        solver.addVariable(name, 1, 10)

    for i, target in enumerate(numbers):
        # The amounts that add up to numbers[i], one for each integer found.
        parts = []
        for j in range(n_integers):
            # use_i_j is 1 when x[j] is one of the integers that add up to numbers[i].
            use = f"use_{i}_{j}"
            solver.addVariable(use, 0, 1)
            # part_i_j is x[j] when it is used for numbers[i], and 0 otherwise.
            part = f"part_{i}_{j}"
            solver.addVariable(part, 0, 10)
            solver.addMultiplication([use, x[j]], True, part, True, part)
            parts.append((1, part))
        # The integers used for numbers[i] add up to it.
        solver.addConstraint(parts, True, target, True, target)

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
