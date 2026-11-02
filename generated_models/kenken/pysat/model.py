# kenken: a PySAT (Python) model from DCP Rosetta.
# Download the `kenken.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python kenken.py kenken.json

from itertools import product

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def cage_holds(digits, target):
    """Does a cage with these digits (in the order of its cells) reach the target? A cage of
    two cells reaches it by sum, product, difference or exact quotient of its digits; a cage
    of any other size by the sum or the product of its digits."""
    if len(digits) == 2:
        a, b = digits
        return (a + b == target or a * b == target or a * target == b
                or b * target == a or a - b == target or b - a == target)
    total, multiplied = 0, 1
    for digit in digits:
        total += digit
        multiplied *= digit
    return total == target or multiplied == target


def create_model(instance):
    """Fill an n by n grid with the digits 1 to n so that every row and column holds each
    digit once, and the digits of each cage achieve the cage's target with its operation."""
    n = instance["n"]            # the grid is n by n, with digits 1..n
    cages = instance["problem"]  # each cage is [target, [[row, col], ...]]: its target and its cells (1-based)

    pool = IDPool()

    # x[r][c] is the digit in the cell at row r, column c (0-based)
    x = [[Integer(f"x_{r}_{c}", 1, n, vpool=pool) for c in range(n)] for r in range(n)]
    engine = IntegerEngine(vars=[cell for row in x for cell in row], vpool=pool)

    # Each row and each column holds each digit exactly once.
    for i in range(n):
        engine.add_alldifferent(x[i])
        engine.add_alldifferent([x[r][i] for r in range(n)])
    formula = engine.clausify()

    # Each cage holds digits that reach its target. The operation is not given, so the digits
    # of a cage may reach it by any operation valid for its size. Digits may repeat in a cage.
    for index, (target, cells) in enumerate(cages):
        # The cells of the cage.
        cage = [x[r - 1][c - 1] for r, c in cells]
        # The digit combinations for the cage that reach its target.
        allowed = [digits for digits in product(range(1, n + 1), repeat=len(cage))
                   if cage_holds(digits, target)]
        # pick[k] is true when the cage takes the k-th allowed combination.
        pick = [pool.id(("cage", index, k)) for k in range(len(allowed))]
        # Some allowed combination is taken. With no allowed combination the cage is impossible.
        formula.append(pick)
        for choice, digits in zip(pick, allowed):
            for cell, digit in zip(cage, digits):
                formula.append([-choice, cell.equals(digit)])

    return formula, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
