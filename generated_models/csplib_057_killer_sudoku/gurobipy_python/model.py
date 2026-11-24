# csplib_057_killer_sudoku: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_057_killer_sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_057_killer_sudoku.py csplib_057_killer_sudoku.json

import math

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Killer sudoku: fill an n-by-n grid with the numbers 1 to n so that every row, every column and every nonet holds each number once, and every cage sums to its total with no number repeated in it."""
    n = instance["n"]  # the grid is n-by-n (9 in the standard puzzle)
    cages = instance["problem"]  # each cage is [total, [[row, col], ...]] with 1-based cells
    box = math.isqrt(n)  # side of a nonet (box-by-box square of cells); 3 for the standard 9-by-9 grid
    cells = range(n)
    values = range(1, n + 1)

    model = gp.Model("killer_sudoku")

    # is_[r, c, v] is 1 when cell (r, c) holds number v (rows and columns counted from 0).
    is_ = model.addVars(cells, cells, values, vtype=GRB.BINARY, name="is")
    # Each cell holds exactly one number (is_.sum(r, c, "*") adds over all numbers).
    model.addConstrs((is_.sum(r, c, "*") == 1 for r in cells for c in cells), name="cell")

    # Each row and each column contains each number exactly once.
    model.addConstrs((is_.sum(r, "*", v) == 1 for v in values for r in cells), name="row")
    model.addConstrs((is_.sum("*", c, v) == 1 for v in values for c in cells), name="col")

    # Each nonet (the 3-by-3 boxes of a 9-by-9 grid) contains each number exactly once.
    model.addConstrs((gp.quicksum(is_[r, c, v] for r in range(br, br + box) for c in range(bc, bc + box)) == 1
                      for br in range(0, n, box) for bc in range(0, n, box) for v in values), name="box")

    # x[r][c] is the number in row r, column c.
    x = [[gp.quicksum(v * is_[r, c, v] for v in values) for c in cells] for r in cells]

    # Each cage: the numbers in it sum to its total (the clue printed in its corner), and no number appears twice in it.
    for k, (total, segment) in enumerate(cages):
        cage = [(r - 1, c - 1) for r, c in segment]
        model.addConstr(gp.quicksum(x[r][c] for r, c in cage) == total, name=f"cage_sum[{k}]")
        model.addConstrs((gp.quicksum(is_[r, c, v] for r, c in cage) <= 1 for v in values),
                         name=f"cage_distinct[{k}]")

    return model, {"x": x}


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
