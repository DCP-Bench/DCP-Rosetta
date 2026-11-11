# flip_rows_cols: a Gurobi (Python) model from DCP Rosetta.
# Download the `flip_rows_cols.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python flip_rows_cols.py flip_rows_cols.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Choose whether to flip the sign of each row and each column of a matrix so that every row and every column sums to a non-negative number, with the overall sum as small as possible."""
    a = instance["input_matrix"]  # a[i][j]: the entry in row i, column j, before any flips
    rows = len(a)
    cols = len(a[0])

    model = gp.Model("flip_rows_cols")

    # row_up[i] is 1 when row i keeps its sign and 0 when it is flipped; col_up[j] likewise
    # for columns. The sign of row i is 2 * row_up[i] - 1, and similarly for columns.
    row_up = [model.addVar(vtype=GRB.BINARY, name=f"row_up[{i}]") for i in range(rows)]
    col_up = [model.addVar(vtype=GRB.BINARY, name=f"col_up[{j}]") for j in range(cols)]

    # flipped[i, j] is 1 when exactly one of row i and column j is flipped, which is when
    # entry (i, j) changes sign. The four constraints below make it the exclusive or of the two up bits.
    flipped = model.addVars(rows, cols, vtype=GRB.BINARY, name="flipped")
    model.addConstrs((flipped[i, j] >= row_up[i] - col_up[j] for i in range(rows) for j in range(cols)),
                     name="xor_a")
    model.addConstrs((flipped[i, j] >= col_up[j] - row_up[i] for i in range(rows) for j in range(cols)),
                     name="xor_b")
    model.addConstrs((flipped[i, j] <= row_up[i] + col_up[j] for i in range(rows) for j in range(cols)),
                     name="xor_c")
    model.addConstrs((flipped[i, j] <= 2 - row_up[i] - col_up[j] for i in range(rows) for j in range(cols)),
                     name="xor_d")

    # x[i, j]: entry (i, j) after the flips, which is a[i][j] or -a[i][j].
    x = {(i, j): a[i][j] * (1 - 2 * flipped[i, j]) for i in range(rows) for j in range(cols)}

    # Every row sum and every column sum is non-negative.
    model.addConstrs((gp.quicksum(x[i, j] for j in range(cols)) >= 0 for i in range(rows)), name="row_nonneg")
    model.addConstrs((gp.quicksum(x[i, j] for i in range(rows)) >= 0 for j in range(cols)), name="col_nonneg")
    # total_sum is the overall sum of all entries after the flips.
    total_sum = gp.quicksum(x.values())
    # Minimise the overall sum of the entries after the flips.
    model.setObjective(total_sum, GRB.MINIMIZE)

    row_signs = [2 * u - 1 for u in row_up]
    col_signs = [2 * u - 1 for u in col_up]
    return model, {"row_signs": row_signs, "col_signs": col_signs}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.Params.MIPGap = 0  # prove the optimum; the default stops within 0.01% of it
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a proven optimum
        print("Objective value:", round(model.ObjVal))
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
