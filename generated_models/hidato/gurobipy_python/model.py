# hidato: a Gurobi (Python) model from DCP Rosetta.
# Download the `hidato.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python hidato.py hidato.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Hidato: fill the grid with the numbers 1 to r*c, keeping the given numbers, so that every
    two consecutive numbers sit in cells that touch horizontally, vertically or diagonally."""
    puzzle = instance["puzzle"]  # puzzle[i][j]: the given number in row i, column j; 0 marks an empty cell
    r = len(puzzle)
    c = len(puzzle[0])
    N = r * c  # the numbers run from 1 to the number of cells
    cells = [(i, j) for i in range(r) for j in range(c)]

    model = gp.Model("hidato")

    # x[i, j] is the number in cell (i, j). A given number fixes the cell; an empty cell can hold 1..N.
    x = {}
    for (i, j) in cells:
        given = puzzle[i][j]
        lo, hi = (given, given) if given > 0 else (1, N)
        x[i, j] = model.addVar(lb=lo, ub=hi, vtype=GRB.INTEGER, name=f"x[{i},{j}]")

    # The numbers are placed as a chain 1, 2, ..., r*c, each next number in a touching cell.
    # next_[p, q] is 1 when cell q holds the number after the one in cell p; it exists only
    # for touching cells (a king's move apart). A one-hot of every number in every cell would
    # need (r*c)**2 binaries, too many for a 12-by-12 grid.
    next_ = {}
    for (i, j) in cells:
        for a in (-1, 0, 1):
            for b in (-1, 0, 1):
                if (a, b) != (0, 0) and 0 <= i + a < r and 0 <= j + b < c:
                    next_[(i, j), (i + a, j + b)] = model.addVar(
                        vtype=GRB.BINARY, name=f"next[{i},{j},{i + a},{j + b}]")

    # When q follows p, the number in q is one more than the number in p.
    model.addConstrs(((next_[p, q] == 1) >> (x[q] == x[p] + 1) for (p, q) in next_),
                     name="consecutive")

    # Each cell has at most one successor and at most one predecessor, and the
    # chain has r*c - 1 links. Numbers grow along every link, so the links hold
    # no loop and form a single chain through all cells; its r*c numbers are
    # consecutive within 1..r*c, so they are all different and start at 1.
    model.addConstrs((gp.quicksum(arc for (s, _), arc in next_.items() if s == p) <= 1
                      for p in cells), name="successor")
    model.addConstrs((gp.quicksum(arc for (_, t), arc in next_.items() if t == p) <= 1
                      for p in cells), name="predecessor")
    model.addConstr(gp.quicksum(next_.values()) == N - 1, name="chain_length")

    return model, {"x": [[x[i, j] for j in range(c)] for i in range(r)]}


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
