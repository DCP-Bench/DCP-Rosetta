# kenken: a cvc5 (Python) model from DCP Rosetta.
# Download the `kenken.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python kenken.py kenken.json

import itertools
import math

import cvc5.pythonic as c5


def create_model(instance):
    """Fill an n by n grid with the digits 1 to n so that every row and column holds each
    digit once, and the digits of each cage achieve the cage's target with its operation."""
    n = instance["n"]            # the grid is n by n, with digits 1..n
    cages = instance["problem"]  # each cage is [target, [[row, col], ...]]: its target and the cells it covers (1-based)
    digits = range(1, n + 1)

    # x[i][j] is the digit in the cell at row i + 1, column j + 1
    x = [[c5.Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    def any_of(options):
        """The one of the options that holds; false when there are no options."""
        if not options:
            return c5.BoolVal(False)
        if len(options) == 1:
            return options[0]
        return c5.Or(options)

    solver = c5.Solver()

    # Each cell holds a digit from 1 to n.
    for row in x:
        for v in row:
            solver.add(v >= 1, v <= n)

    # Each row holds each digit exactly once.
    solver.add([c5.Distinct(row) for row in x])

    # Each column holds each digit exactly once.
    solver.add([c5.Distinct(list(col)) for col in zip(*x)])

    # Each cage achieves its target. The operation is not given, so a cage may use any
    # operation that is valid for its size. Digits may repeat within a cage.
    for target, cells in cages:
        cage = [x[r - 1][c - 1] for r, c in cells]
        if len(cage) == 1:
            solver.add(cage[0] == target)
        elif len(cage) == 2:
            # Two cells: their digits form a pair whose sum, difference, product or exact
            # quotient (either order) is the target.
            pairs = [
                (a, b)
                for a in digits
                for b in digits
                if a + b == target or abs(a - b) == target or a * b == target
                or a == b * target or b == a * target
            ]
            solver.add(any_of([c5.And(cage[0] == a, cage[1] == b) for a, b in pairs]))
        else:
            # Three or more cells: the digits sum to the target, or they multiply to it.
            # The digit tuples that multiply to the target.
            tuples = [
                tup for tup in itertools.product(digits, repeat=len(cage))
                if math.prod(tup) == target
            ]
            solver.add(any_of(
                [c5.Sum(cage) == target]
                + [c5.And([v == d for v, d in zip(cage, tup)]) for tup in tuples]
            ))

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
