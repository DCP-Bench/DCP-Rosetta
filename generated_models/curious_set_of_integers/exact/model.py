# curious_set_of_integers: an Exact (Python) model from DCP Rosetta.
# Download the `curious_set_of_integers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python curious_set_of_integers.py curious_set_of_integers.json

from math import isqrt

from exact import Exact


def create_model(instance):
    """The integers 1, 3, 8 and 120 form a set in which the product of any two
    integers is one less than a perfect square. Find a fifth number (at least 0)
    that can be added to the set without destroying this property."""
    n_numbers = instance["n"]      # the number of integers in the set, including the one to find
    max_val = instance["max_val"]  # the largest value an integer of the set may take
    given = [1, 3, 8, 120]         # the integers of the set given in the puzzle

    solver = Exact()

    # Exact identifies its variables by name.
    # x[i] is the i-th integer of the set. The given integers come first and are fixed,
    # and the last one is the number to find.
    x = [f"x_{i}" for i in range(n_numbers)]
    # top[i] is the largest value x[i] can take
    top = []
    for i in range(n_numbers):
        if i < len(given):
            low, high = given[i], given[i]
        else:
            low, high = 0, max_val
        top.append(high)
        solver.addVariable(x[i], low, high)

    # All integers of the set differ. For each pair, above is 1 when x_i is the larger one
    # and 0 when x_j is. big is larger than any difference between two integers of the set,
    # so the comparison that does not hold is switched off.
    big = max_val + 1
    for i in range(n_numbers):
        for j in range(i + 1, n_numbers):
            above = f"x_{i}_above_x_{j}"
            solver.addVariable(above, 0, 1)
            # If above is 1, x_i is at least one more than x_j.
            solver.addConstraint([(1, x[i]), (-1, x[j]), (-big, above)], True, 1 - big)
            # If above is 0, x_j is at least one more than x_i.
            solver.addConstraint([(1, x[j]), (-1, x[i]), (big, above)], True, 1)

    # For each pair, the product of the two integers is one less than a perfect square:
    # square is the product plus one, and root is the square root of square. The largest
    # root is the square root of the largest product plus one.
    for i in range(n_numbers):
        for j in range(i + 1, n_numbers):
            p_max = isqrt(top[i] * top[j] + 1)
            root, square, product = f"root_{i}_{j}", f"root_squared_{i}_{j}", f"product_{i}_{j}"
            solver.addVariable(root, 0, p_max)
            solver.addVariable(square, 0, p_max * p_max)
            solver.addVariable(product, 0, top[i] * top[j])
            solver.addMultiplication([root, root], True, square, True, square)
            solver.addMultiplication([x[i], x[j]], True, product, True, product)
            solver.addConstraint([(1, square), (-1, product)], True, 1, True, 1)

    return solver, {"number": x[-1]}


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
