# csplib_054_n_queens: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_054_n_queens.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_054_n_queens.py csplib_054_n_queens.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """N-queens: place n queens on an n-by-n board so that no two share a row, a column or a diagonal."""
    n = instance["n"]  # the board is n by n, with one queen in each row
    rows = range(n)
    cols = range(n)

    model = gp.Model("n_queens")

    # queen[i, j] is 1 when the queen of row i stands in column j (both counted from 0).
    queen = model.addVars(rows, cols, vtype=GRB.BINARY, name="queen")

    # Every row has exactly one queen.
    model.addConstrs((queen.sum(i, "*") == 1 for i in rows), name="row")

    # No two queens share a column.
    model.addConstrs((queen.sum("*", j) <= 1 for j in cols), name="col")

    # No two queens share a diagonal: squares with the same j - i lie on one
    # diagonal, and squares with the same j + i on one anti-diagonal.
    model.addConstrs((gp.quicksum(queen[i, i + d] for i in rows if 0 <= i + d < n) <= 1
                      for d in range(-(n - 1), n)), name="diag")
    model.addConstrs((gp.quicksum(queen[i, s - i] for i in rows if 0 <= s - i < n) <= 1
                      for s in range(2 * n - 1)), name="anti")

    # queens[i] is the 1-based column of the queen in row i.
    return model, {"queens": [gp.quicksum((j + 1) * queen[i, j] for j in cols) for i in rows]}


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
