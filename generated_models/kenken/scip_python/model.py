# kenken: a SCIP (Python) model from DCP Rosetta.
# Download the `kenken.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python kenken.py kenken.json

import math

import numpy as np
from pyscipopt import Model, quicksum


def create_model(instance):
    """KenKen on an n x n grid. Fill the grid with the digits 1 to n so that every row and
    every column holds each digit exactly once, and every cage (a group of cells with a
    target number) reaches its target with one arithmetic operation on its digits. The
    operation of a cage is not given in the data, so the model lets the solver choose one
    that fits. A single-cell cage holds its target. Sum and product apply to cages of any
    size; difference and exact quotient apply to two-cell cages only, as in the usual KenKen
    rule. Digits may repeat inside a cage."""
    n = instance["n"]  # the grid is n x n, and its digits are 1 to n, as the statement says
    cages = instance["problem"]  # the cages: each is [target, [[row, column], ...]], counted from 1

    model = Model("kenken")

    # x[r, c] is the digit in row r and column c, an integer from 1 to n (0-based r and c).
    # It is an integer, not only one-hot, because the cage operations are sums and products
    # of these digits.
    x = model.addMatrixVar((n, n), vtype="I", lb=1, ub=n, name="x")

    # y[r, c, d] is 1 when cell (r, c) holds the digit d + 1: the one-hot form of x. SCIP has
    # no all-different constraint and no !=, so each row and column holding each digit once
    # is written as a linear sum equal to 1 per digit, which is stronger than pairwise !=.
    y = model.addMatrixVar((n, n, n), vtype="B", name="y")
    digits = np.arange(1, n + 1)  # digits[d] is the value of one-hot position d
    model.addMatrixCons(x == (y * digits).sum(axis=2))  # x is the digit the one-hot choice selects
    model.addMatrixCons(y.sum(axis=2) == 1)  # each cell holds exactly one digit
    model.addMatrixCons(y.sum(axis=1) == 1)  # each row holds each digit exactly once
    model.addMatrixCons(y.sum(axis=0) == 1)  # each column holds each digit exactly once

    for j, (target, cells) in enumerate(cages):
        digit = [x[r - 1, c - 1] for r, c in cells]  # the digits of this cage's cells

        if len(cells) == 1:
            # A single-cell cage: its digit is its target, and no operation is involved.
            model.addCons(digit[0] == target)
            continue

        # The product of the digits is not linear, and addConsIndicator needs a linear left
        # side, so the product is held in the integer prod_j, tied to it by one nonlinear
        # equality. Its bounds 1 and n**k are the smallest and largest product of k digits
        # in 1 to n, with k the number of cells in the cage.
        prod = model.addVar(vtype="I", lb=1, ub=n ** len(cells), name=f"prod_{j}")
        model.addCons(prod == math.prod(digit))

        # The operations this cage may use, each as an equality lhs == rhs that must hold
        # when the operation is chosen. Sum and product apply to any cage. Difference and
        # quotient relate two cells, so they apply to two-cell cages only.
        options = [
            (quicksum(digit), target),  # the digits add up to the target
            (prod, target),  # the digits multiply to the target
        ]
        if len(cells) == 2:
            a, b = digit
            options += [
                (a - b, target),  # the first digit exceeds the second by the target
                (b - a, target),  # the second digit exceeds the first by the target
                (a - target * b, 0),  # the first digit is the target times the second: exact quotient
                (b - target * a, 0),  # the second digit is the target times the first: exact quotient
            ]

        # Exactly one operation holds for the cage. For a pair, the choice of difference or
        # quotient also says which cell is the larger one, or the multiple of the other.
        choice = [model.addVar(vtype="B", name=f"op_{j}_{i}") for i in range(len(options))]
        model.addCons(quicksum(choice) == 1)
        # Each equality holds when its binary is 1. addConsIndicator takes an inequality, not
        # an equality, so the equality is posted as two indicators on the same binary.
        for pick, (lhs, rhs) in zip(choice, options):
            model.addConsIndicator(lhs <= rhs, binvar=pick)
            model.addConsIndicator(lhs >= rhs, binvar=pick)

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
