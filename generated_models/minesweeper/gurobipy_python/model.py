# minesweeper: a Gurobi (Python) model from DCP Rosetta.
# Download the `minesweeper.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python minesweeper.py minesweeper.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Decide which of the X fields (unopened cells) of a minesweeper board hold mines, so that the number on every opened cell is the count of mines among its up to eight neighbours."""
    unopened = instance["X"]  # the value that marks an unopened, 'X', cell (-1 in the data)
    game = instance["game_data"]  # game[r][c]: the number shown on the cell in row r, column c, or unopened
    rows = len(game)
    cols = len(game[0])

    model = gp.Model("minesweeper")

    # mines[r, c] is 1 when the cell in row r, column c holds a mine, and 0 when not.
    mines = model.addVars(rows, cols, vtype=GRB.BINARY, name="mines")

    # The opened cells are those that show a number.
    opened = [(r, c) for r in range(rows) for c in range(cols) if game[r][c] != unopened]
    # An opened cell shows a number, so it cannot hold a mine.
    model.addConstrs((mines[r, c] == 0 for r, c in opened), name="open")
    # The number on an opened cell is the count of mines among its neighbours: the cells around it
    # (up to eight, only those on the board).
    model.addConstrs((gp.quicksum(mines[r + a, c + b]
                                  for a in (-1, 0, 1) for b in (-1, 0, 1)
                                  if (a, b) != (0, 0) and 0 <= r + a < rows and 0 <= c + b < cols)
                      == game[r][c] for r, c in opened), name="count")

    # No objective: any board that fits the numbers is a solution.
    # mines[r][c] is the cell's variable, so the output is the board of mine flags.
    return model, {"mines": [[mines[r, c] for c in range(cols)] for r in range(rows)]}


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
