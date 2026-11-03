# kenken: a Z3 (Python) model from DCP Rosetta.
# Download the `kenken.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python kenken.py kenken.json

import z3


def create_model(instance):
    """Fill an n by n grid with the digits 1 to n so that every row and column holds each
    digit once, and the digits of each cage achieve the cage's target with its operation."""
    n = instance["n"]            # the grid is n by n, with digits 1 to n
    cages = instance["problem"]  # each cage is [target, [[row, col], ...]]: its target and the cells it covers, counted from 1

    # x[r][c] is the digit in the cell at row r, column c
    x = [[z3.Int(f"x_{r}_{c}") for c in range(n)] for r in range(n)]

    solver = z3.Solver()

    # Every cell holds a digit from 1 to n.
    for r in range(n):
        for c in range(n):
            solver.add(x[r][c] >= 1, x[r][c] <= n)

    # Each row holds each digit exactly once.
    solver.add([z3.Distinct(row) for row in x])

    # Each column holds each digit exactly once.
    solver.add([z3.Distinct([x[r][c] for r in range(n)]) for c in range(n)])

    # Each cage achieves its target. The operation is not given, so a cage may use any
    # operation that is valid for its size. Digits may repeat within a cage.
    for target, cells in cages:
        cage = [x[r - 1][c - 1] for r, c in cells]
        if len(cage) == 2:
            a, b = cage
            # Two cells: their sum, product, difference (either order) or exact quotient
            # (either order) equals the target.
            solver.add(z3.Or(
                a + b == target,
                a * b == target,
                a - b == target,
                b - a == target,
                a * target == b,
                b * target == a,
            ))
        else:
            # The product of the digits in the cage.
            product = cage[0]
            for cell in cage[1:]:
                product = product * cell
            # Three or more cells: the sum or the product of the digits equals the target.
            solver.add(z3.Or(z3.Sum(cage) == target, product == target))

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
