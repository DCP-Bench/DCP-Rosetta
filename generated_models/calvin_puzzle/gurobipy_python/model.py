# calvin_puzzle: a Gurobi (Python) model from DCP Rosetta.
# Download the `calvin_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python calvin_puzzle.py calvin_puzzle.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Calvin puzzle: write the numbers 1 to n^2 on an n-by-n grid, each square once, so that each number
    is three squares from the previous one along a row or column, or two squares from it diagonally."""
    n = instance["n"]  # the side of the grid: n rows and n columns of squares
    cells = [(i, j) for i in range(n) for j in range(n)]  # the squares, as (row, column)
    last = n * n  # the largest number, written on one square each

    # The moves the statement allows from one square to the square of the next number: three
    # squares vertically or horizontally (Type I), or two squares diagonally (Type II).
    moves = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]
    # A step is an arc (i, j, k, l): the square (k, l) is one of the moves from the square (i, j).
    arcs = [(i, j, i + a, j + b) for (i, j) in cells for (a, b) in moves
            if 0 <= i + a < n and 0 <= j + b < n]

    model = gp.Model("calvin_puzzle")

    # x[i, j] is the number written on the square in row i, column j, from 1 to n^2.
    x = model.addVars(cells, lb=1, ub=last, vtype=GRB.INTEGER, name="x")

    # next_[i, j, k, l] is 1 when the number after the one on square (i, j) is written on square (k, l).
    # Only the moves above are arcs, which is far fewer variables than a position for every number.
    next_ = model.addVars(arcs, vtype=GRB.BINARY, name="next")

    # Each square is followed by at most one square and preceded by at most one.
    model.addConstrs((next_.sum(i, j, "*", "*") <= 1 for (i, j) in cells), name="out")
    model.addConstrs((next_.sum("*", "*", i, j) <= 1 for (i, j) in cells), name="in")
    # There are n^2 - 1 steps between the n^2 consecutive numbers, so n^2 - 1 steps are taken.
    model.addConstr(next_.sum() == last - 1, name="steps")

    # A step from square (i, j) to square (k, l) means (k, l) holds the next number. Because the numbers
    # rise by one along every step, the steps cannot close up into a loop.
    model.addConstrs(((next_[i, j, k, l] == 1) >> (x[k, l] == x[i, j] + 1)
                      for (i, j, k, l) in arcs), name="step")

    # The sequence starts at 1: a square that no step enters holds 1. Exactly one square has no entering
    # step, since the n^2 - 1 steps form one path through all the squares.
    model.addConstrs((x[i, j] <= 1 + (last - 1) * next_.sum("*", "*", i, j) for (i, j) in cells),
                     name="start")

    return model, {"x": [[x[i, j] for j in range(n)] for i in range(n)]}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
