# kenken: a CPMpy model from DCP Rosetta.
# Download the `kenken.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python kenken.py kenken.json

import cpmpy as cp


def create_model(instance):
    """Fill an n by n grid with the digits 1 to n so that every row and column holds each
    digit once, and the digits of each cage achieve the cage's target with its operation."""
    n = instance["n"]              # the grid is n by n, with digits 1..n
    cages = instance["problem"]    # each cage is [target, [[row, col], ...]]: its target and its cells (1-based)

    # x[i, j] is the digit in the cell at row i, column j (0-based)
    x = cp.intvar(1, n, shape=(n, n), name="x")

    model = cp.Model()

    # Each row holds each digit exactly once.
    model.add([cp.AllDifferent(row) for row in x])

    # Each column holds each digit exactly once.
    model.add([cp.AllDifferent(col) for col in x.T])

    # Each cage achieves its target. The operation is not given, so a cage may use any
    # operation that is valid for its size. Digits may repeat within a cage.
    for target, cells in cages:
        cage = cp.cpm_array([x[r - 1, c - 1] for r, c in cells])
        if len(cells) == 2:
            # Two cells: their sum, product, difference (either order) or exact quotient
            # (either order) equals the target.
            a, b = cage
            model.add((a + b == target)
                | (a * b == target)
                | (a - b == target)
                | (b - a == target)
                | (a * target == b)
                | (b * target == a))
        else:
            # Three or more cells: subtraction and division are only defined for two cells,
            # so the sum or the product of the digits equals the target.
            model.add((cp.sum(cage) == target) | (cage.prod() == target))

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
