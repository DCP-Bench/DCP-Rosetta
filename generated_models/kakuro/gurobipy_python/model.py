# kakuro: a Gurobi (Python) model from DCP Rosetta.
# Download the `kakuro.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python kakuro.py kakuro.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Fill the white cells of a Kakuro grid with digits 1 to 9 so that each run of white cells sums to its clue and no digit repeats within a run."""
    n = instance["n"]  # the grid is n by n cells
    entries = instance["problem"]  # entries[k] is [clue, [row, col], ...]: the clue of run k, then its cells (1-based)
    blanks = instance["blanks"]  # blanks[k] is [row, col], 1-based: a cell that is not white, so it holds 0
    cells = range(n)  # row and column numbers, 0-based
    digits = range(10)  # 0 stands for a blank cell; 1 to 9 are the digits to place (from the statement)

    model = gp.Model("kakuro")

    # is_[r, c, d] is 1 when cell (r, c) holds digit d, and 0 when not (0-based cells)
    is_ = model.addVars(cells, cells, digits, vtype=GRB.BINARY, name="is")
    # Every cell holds exactly one value: the sum over all digits (the "*") is 1.
    model.addConstrs((is_.sum(r, c, "*") == 1 for r in cells for c in cells), name="one_value")
    # x[r][c] is the digit in cell (r, c), 0 for a blank cell
    x = [[gp.quicksum(d * is_[r, c, d] for d in digits) for c in cells] for r in cells]

    # The cells that are not white hold 0.
    model.addConstrs((is_[r - 1, c - 1, 0] == 1 for r, c in blanks), name="blank")

    for entry in entries:
        clue = entry[0]  # the digits of this run must sum to the clue
        run = [(r - 1, c - 1) for r, c in entry[1:]]  # the cells of the run, 0-based
        # The cells of a run are white, so each holds a digit 1 to 9, not 0.
        model.addConstrs((is_[r, c, 0] == 0 for r, c in run), name="white")
        # The digits of the run sum to its clue.
        model.addConstr(gp.quicksum(x[r][c] for r, c in run) == clue, name="clue")
        # No digit 1 to 9 appears more than once in the run.
        model.addConstrs((gp.quicksum(is_[r, c, d] for r, c in run) <= 1 for d in range(1, 10)), name="distinct")

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
