# curious_set_of_integers: a Z3 (Python) model from DCP Rosetta.
# Download the `curious_set_of_integers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python curious_set_of_integers.py curious_set_of_integers.json

import z3


def create_model(instance):
    """The integers 1, 3, 8 and 120 form a set in which the product of any two
    integers is one less than a perfect square. Find a fifth number (at least 0)
    that can be added to the set without destroying this property."""
    n = instance["n"]              # the number of integers in the set, including the one to find
    max_val = instance["max_val"]  # the largest value an integer in the set may take

    # The integers 1, 3, 8 and 120 of the puzzle
    given = [1, 3, 8, 120]

    # The number of bits that holds an integer from 0 to max_val
    bits = max_val.bit_length()
    # The number of bits that holds the product of two such integers, plus one
    wide = 2 * bits + 1

    # v, with enough leading zeros to hold a product of two such integers
    def widen(v):
        return z3.ZeroExt(wide - bits, v)

    # x[i] is the i-th integer of the set; the last one is the number to find
    x = [z3.BitVec(f"x_{i}", bits) for i in range(n)]
    number = x[n - 1]

    solver = z3.Solver()

    # Every integer of the set lies between 0 and max_val.
    solver.add([z3.ULE(v, max_val) for v in x])

    # The integers of the set are all different.
    solver.add(z3.Distinct(x))

    # The set starts with the given integers.
    solver.add([member == value for member, value in zip(x, given)])

    # For each pair of integers in the set, the product plus one is a perfect square.
    # root is the square root of that sum, and it is at most max_val.
    for i in range(n):
        for j in range(i + 1, n):
            root = z3.BitVec(f"root_{i}_{j}", bits)
            solver.add(z3.ULE(root, max_val))
            solver.add(widen(root) * widen(root) == widen(x[i]) * widen(x[j]) + 1)

    return solver, {"number": z3.BV2Int(number)}


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
