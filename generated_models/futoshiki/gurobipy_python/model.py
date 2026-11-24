# futoshiki: a Gurobi (Python) model from DCP Rosetta.
# Download the `futoshiki.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python futoshiki.py futoshiki.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Futoshiki: fill a size-by-size grid with the numbers 1 to size so that each row and each column
    holds every number once, the numbers given at the start stay, and every given inequality holds."""
    values = instance["values"]  # values[r][c]: the number given in row r, column c (0-based), 0 when empty
    lt = instance["lt"]  # lt[k] = [i1, j1, i2, j2], 1-based: cell (i1, j1) is smaller than cell (i2, j2)
    size = len(values)  # the grid is size by size
    cells = range(size)  # rows and columns, 0-based
    digits = range(1, size + 1)  # the numbers 1 to size

    model = gp.Model("futoshiki")

    # holds[r, c, v] is 1 when cell (r, c) holds the number v.
    holds = model.addVars(cells, cells, digits, vtype=GRB.BINARY, name="holds")
    # Each cell holds exactly one number.
    model.addConstrs((holds.sum(r, c, "*") == 1 for r in cells for c in cells), name="cell")
    # grid[r][c] is the number in row r, column c.
    grid = [[gp.quicksum(v * holds[r, c, v] for v in digits) for c in cells] for r in cells]

    # The numbers given at the start keep their values.
    model.addConstrs((holds[r, c, values[r][c]] == 1 for r in cells for c in cells if values[r][c] > 0),
                     name="given")

    # Each row and each column contains each number exactly once.
    model.addConstrs((holds.sum(r, "*", v) == 1 for r in cells for v in digits), name="row")
    model.addConstrs((holds.sum("*", c, v) == 1 for c in cells for v in digits), name="col")

    # Each given inequality between two cells holds (the first cell is the smaller one).
    model.addConstrs((grid[i1 - 1][j1 - 1] <= grid[i2 - 1][j2 - 1] - 1
                      for k, (i1, j1, i2, j2) in enumerate(lt)), name="less")

    return model, {"grid": grid}


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
