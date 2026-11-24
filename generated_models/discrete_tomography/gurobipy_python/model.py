# discrete_tomography: a Gurobi (Python) model from DCP Rosetta.
# Download the `discrete_tomography.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python discrete_tomography.py discrete_tomography.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Discrete tomography: rebuild a 0/1 matrix from the number of ones in each row and each column."""
    row_sums = instance["row_sums"]  # row_sums[i]: the number of ones in row i
    col_sums = instance["col_sums"]  # col_sums[j]: the number of ones in column j
    rows = range(len(row_sums))
    cols = range(len(col_sums))

    model = gp.Model("discrete_tomography")

    # matrix[i, j] is 1 when the entry in row i, column j is a one, and 0 when it is a zero.
    matrix = model.addVars(rows, cols, vtype=GRB.BINARY, name="matrix")

    # Each row holds as many ones as its x-ray says (matrix.sum(i, "*") adds up row i).
    model.addConstrs((matrix.sum(i, "*") == row_sums[i] for i in rows), name="row")
    # Each column holds as many ones as its x-ray says (matrix.sum("*", j) adds up column j).
    model.addConstrs((matrix.sum("*", j) == col_sums[j] for j in cols), name="col")

    # The matrix is returned as a list of rows.
    return model, {"matrix": [[matrix[i, j] for j in cols] for i in rows]}


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
