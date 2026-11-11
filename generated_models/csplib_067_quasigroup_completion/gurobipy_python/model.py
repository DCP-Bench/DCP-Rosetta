# csplib_067_quasigroup_completion: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_067_quasigroup_completion.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_067_quasigroup_completion.py csplib_067_quasigroup_completion.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Complete a partially filled quasigroup: an N-by-N multiplication table in which every
    row and every column holds each of the values 1 to N exactly once."""
    N = instance["N"]          # the order of the quasigroup: N rows, N columns and N values
    start = instance["start"]  # start[i][j]: the value given in row i, column j; 0 marks an empty cell
    cells = range(N)           # the rows and the columns, numbered from 0
    values = range(1, N + 1)   # the values 1 to N, from the statement

    model = gp.Model("quasigroup_completion")

    # holds[i, j, v] is 1 when the cell in row i, column j holds the value v; 0 otherwise.
    holds = model.addVars(cells, cells, values, vtype=GRB.BINARY, name="holds")
    # Each cell holds exactly one value (holds.sum(i, j, "*") adds holds[i, j, v] over all v).
    model.addConstrs((holds.sum(i, j, "*") == 1 for i in cells for j in cells), name="cell")

    # A pre-filled cell keeps its starting value.
    model.addConstrs((holds[i, j, start[i][j]] == 1 for i in cells for j in cells
                      if start[i][j] != 0), name="given")

    # Each row and each column contains each value exactly once (holds.sum(i, "*", v) adds
    # holds[i, j, v] over all columns j, and holds.sum("*", j, v) over all rows i).
    model.addConstrs((holds.sum(i, "*", v) == 1 for i in cells for v in values), name="row")
    model.addConstrs((holds.sum("*", j, v) == 1 for j in cells for v in values), name="col")

    # No objective: any completed square that meets the constraints answers the puzzle.

    # The completed square: puzzle[i][j] is the value in row i, column j, as lists over the rows and columns.
    puzzle = [[gp.quicksum(v * holds[i, j, v] for v in values) for j in cells] for i in cells]
    return model, {"puzzle": puzzle}


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
