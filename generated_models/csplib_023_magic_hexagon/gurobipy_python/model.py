# csplib_023_magic_hexagon: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_023_magic_hexagon.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_023_magic_hexagon.py csplib_023_magic_hexagon.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Magic hexagon: place the numbers 1 to NUM_CELLS in a hexagon so that every row and
    every diagonal line adds up to the same magic sum."""
    cells_count = instance["NUM_CELLS"]  # NUM_CELLS: how many cells, 19, which hold the numbers 1..19
    magic = instance["MAGIC_SUM"]        # MAGIC_SUM: the sum every line must reach, 38

    # A hexagon of side s has 3s^2 - 3s + 1 cells (19 for s = 3); find the side from the cell count.
    side = 1
    while 3 * side * side - 3 * side + 1 < cells_count:
        side += 1
    if 3 * side * side - 3 * side + 1 != cells_count:
        raise ValueError("NUM_CELLS is not the size of a hexagon")

    # Cells in reading order (A, B, C on the top row, then D..G, ...), in axial
    # coordinates (q, r): r is the row, and the two diagonal directions are the
    # lines of constant q and of constant q + r.
    rad = side - 1
    cells = [(q, r) for r in range(-rad, rad + 1)
             for q in range(max(-rad, -rad - r), min(rad, rad - r) + 1)]
    values = range(1, cells_count + 1)

    model = gp.Model("magic_hexagon")

    # put[c, v] = 1 when cell c holds number v; LD[c] reads the number back.
    put = model.addVars(len(cells), values, vtype=GRB.BINARY, name="put")
    LD = [gp.quicksum(v * put[c, v] for v in values) for c in range(len(cells))]

    # Each cell holds exactly one number.
    model.addConstrs((put.sum(c, "*") == 1 for c in range(len(cells))), name="one_number")
    # Each of the numbers 1..NUM_CELLS is used in exactly one cell.
    model.addConstrs((put.sum("*", v) == 1 for v in values), name="used_once")

    # The lines of the hexagon: its rows, and its diagonals in both directions (15 lines in all).
    lines = {}
    for c, (q, r) in enumerate(cells):
        for key in (("row", r), ("diag", q), ("anti", q + r)):
            lines.setdefault(key, []).append(c)
    # Every line adds up to the magic sum.
    model.addConstrs((gp.quicksum(LD[c] for c in lines[key]) == magic for key in lines),
                     name="magic_sum")

    return model, {"LD": LD}


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
