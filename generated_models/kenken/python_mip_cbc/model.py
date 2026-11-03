# kenken: a Python-MIP (Python) model from DCP Rosetta.
# Download the `kenken.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python kenken.py kenken.json

import itertools

import mip


def achieves(digits, target):
    """True when one operation on the digits of a cage gives its target: their sum, their
    product, and for a pair also their difference or their quotient."""
    if sum(digits) == target:
        return True
    # the product of all the digits
    product = 1
    for d in digits:
        product *= d
    if product == target:
        return True
    if len(digits) == 2:
        a, b = digits
        if abs(a - b) == target:
            return True
        hi, lo = max(a, b), min(a, b)
        if hi % lo == 0 and hi // lo == target:
            return True
    return False


def create_model(instance):
    """Fill an n by n grid with the digits 1 to n so that each row and each column holds
    every digit once, and the digits of each cage achieve the cage's target under an
    operation that is not given. Digits may repeat within a cage."""
    n = instance["n"]              # the grid is n by n
    cages = instance["problem"]    # each cage is its target followed by the cells it covers

    # the digits that fill the grid
    values = list(range(1, n + 1))

    model = mip.Model(solver_name="CBC")

    # holds[r][c][v - 1] is 1 when cell (r, c) holds digit v, and 0 when not
    holds = [[[model.add_var(var_type=mip.BINARY) for _ in values]
              for _ in range(n)] for _ in range(n)]
    # digit[r][c] is the digit in cell (r, c)
    digit = [[model.add_var(lb=1, ub=n, var_type=mip.INTEGER) for _ in range(n)]
             for _ in range(n)]
    for r in range(n):
        for c in range(n):
            # Each cell holds exactly one digit.
            model.add_constr(mip.xsum(holds[r][c]) == 1)
            # The digit of the cell is the one it holds.
            model.add_constr(digit[r][c] == mip.xsum(v * holds[r][c][v - 1] for v in values))

    # Each row holds each digit exactly once.
    for r in range(n):
        for v in values:
            model.add_constr(mip.xsum(holds[r][c][v - 1] for c in range(n)) == 1)

    # Each column holds each digit exactly once.
    for c in range(n):
        for v in values:
            model.add_constr(mip.xsum(holds[r][c][v - 1] for r in range(n)) == 1)

    # Each cage takes one digit tuple that achieves its target, and each of its cells
    # holds the digit that the tuple gives it.
    for target, cells in cages:
        # the cells of the cage as (row, col) positions
        positions = [(r - 1, c - 1) for r, c in cells]
        # the digit tuples that achieve the cage's target, one digit per cell
        tuples = [combo for combo in itertools.product(values, repeat=len(positions))
                  if achieves(combo, target)]
        if not tuples:
            # No digit tuple fits this cage, so no grid can satisfy it.
            dummy = model.add_var(var_type=mip.BINARY)
            model.add_constr(dummy == 1)
            model.add_constr(dummy == 0)
            continue
        # pick[j] is 1 when the cage takes the j-th digit tuple
        pick = [model.add_var(var_type=mip.BINARY) for _ in tuples]
        model.add_constr(mip.xsum(pick) == 1)
        for j, combo in enumerate(tuples):
            for (r, c), d in zip(positions, combo):
                model.add_constr(pick[j] <= holds[r][c][d - 1])

    return model, {"x": digit}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
