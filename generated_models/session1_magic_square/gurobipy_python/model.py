# session1_magic_square: a Gurobi (Python) model from DCP Rosetta.
# Download the `session1_magic_square.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python session1_magic_square.py session1_magic_square.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Fill an n-by-n grid with the numbers 1 to n^2, each used once, so that every row, every column and both diagonals add up to the same magic sum."""
    n = instance["n"]  # the side of the square
    values = range(1, n * n + 1)
    # The magic sum n(n^2 + 1)/2, from the statement.
    magic_sum = n * (n * n + 1) // 2

    model = gp.Model("magic_square")

    # holds[i, j, v] is 1 when the cell in row i, column j (counted from 0) contains the number v.
    holds = model.addVars(range(n), range(n), values, vtype=GRB.BINARY, name="holds")
    # square[i][j] is the number in row i, column j, read back from holds.
    square = [[gp.quicksum(v * holds[i, j, v] for v in values) for j in range(n)] for i in range(n)]

    # Every cell holds exactly one number: holds.sum(i, j, "*") adds holds[i, j, v] over all v.
    model.addConstrs((holds.sum(i, j, "*") == 1 for i in range(n) for j in range(n)), name="one_number")

    # Each number from 1 to n^2 is in exactly one cell, so all the numbers in the square are different.
    model.addConstrs((holds.sum("*", "*", v) == 1 for v in values), name="each_number_once")

    # Every row, every column and both diagonals add up to the magic sum.
    model.addConstrs((gp.quicksum(square[i]) == magic_sum for i in range(n)), name="row")
    model.addConstrs((gp.quicksum(row[j] for row in square) == magic_sum for j in range(n)), name="column")
    model.addConstr(gp.quicksum(square[i][i] for i in range(n)) == magic_sum, name="diagonal")
    model.addConstr(gp.quicksum(square[i][n - 1 - i] for i in range(n)) == magic_sum, name="other_diagonal")

    return model, {"square": square}


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
