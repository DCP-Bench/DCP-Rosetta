# sudoku: a Gurobi (Python) model from DCP Rosetta.
# Download the `sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python sudoku.py sudoku.json

import gurobipy as gp
from gurobipy import GRB

# The grid, its boxes and its digits are fixed by the rules of Sudoku.
SIZE, BOX = 9, 3
CELLS = range(SIZE)
DIGITS = range(1, SIZE + 1)


def create_model(instance):
    """Fill a 9-by-9 grid with the digits 1 to 9 so that every row, every column and every
    3-by-3 box holds each digit exactly once, keeping the digits that are already given."""
    given = instance["input_grid"]  # given[r][c]: the digit given in row r, column c, or 0 when empty

    model = gp.Model("sudoku")

    # holds[r, c, d] is 1 when the cell in row r, column c holds digit d.
    holds = model.addVars(CELLS, CELLS, DIGITS, vtype=GRB.BINARY, name="holds")

    # Every cell holds exactly one digit (holds.sum(r, c, "*") adds holds[r, c, d] over all digits d).
    model.addConstrs((holds.sum(r, c, "*") == 1 for r in CELLS for c in CELLS), name="cell")

    # A given digit stays in its cell.
    model.addConstrs((holds[r, c, given[r][c]] == 1 for r in CELLS for c in CELLS
                      if given[r][c] != 0), name="given")

    # Each digit appears once in every row (holds.sum(r, "*", d) adds over all columns c).
    model.addConstrs((holds.sum(r, "*", d) == 1 for r in CELLS for d in DIGITS), name="row")
    # Each digit appears once in every column (holds.sum("*", c, d) adds over all rows r).
    model.addConstrs((holds.sum("*", c, d) == 1 for c in CELLS for d in DIGITS), name="col")

    # Each digit appears once in every 3-by-3 box.
    model.addConstrs((gp.quicksum(holds[r, c, d] for r in range(top, top + BOX)
                                  for c in range(left, left + BOX)) == 1
                      for top in range(0, SIZE, BOX) for left in range(0, SIZE, BOX)
                      for d in DIGITS), name="box")

    # grid[r][c] is the digit in row r, column c, read from the digit chosen in that cell.
    grid = [[gp.quicksum(d * holds[r, c, d] for d in DIGITS) for c in CELLS] for r in CELLS]
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
