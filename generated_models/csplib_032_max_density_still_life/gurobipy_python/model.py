# csplib_032_max_density_still_life: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_032_max_density_still_life.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_032_max_density_still_life.py csplib_032_max_density_still_life.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Maximum density still life: the most live cells in an n x m Game of Life pattern that does not change, with all cells outside the grid dead."""
    n = instance["n"]  # the number of rows of the active grid
    m = instance["m"]  # the number of columns of the active grid

    model = gp.Model("still_life")

    # grid[i, j] is 1 when cell (i, j) is alive.
    grid = model.addVars(n, m, vtype=GRB.BINARY, name="grid")

    for i in range(n):
        for j in range(m):
            neighbours = [grid[i + di, j + dj] for di in (-1, 0, 1) for dj in (-1, 0, 1)
                          if (di, dj) != (0, 0) and 0 <= i + di < n and 0 <= j + dj < m]
            k = len(neighbours)      # number of neighbours inside the grid
            live = gp.quicksum(neighbours)  # number of live neighbours of cell (i, j)

            # A live cell has at least 2 live neighbours.
            model.addConstr(live >= 2 * grid[i, j], name=f"live_lo[{i},{j}]")
            # A live cell has at most 3 live neighbours (this only binds when the cell has more than 3 neighbours).
            if k > 3:
                model.addConstr(live <= 3 + (k - 3) * (1 - grid[i, j]), name=f"live_hi[{i},{j}]")

            # A dead cell must not have exactly 3 live neighbours: it has at most 2
            # (fewer) or at least 4 (more). fewer[i, j] and more[i, j] are auxiliary
            # binaries that record which of the two cases holds.
            if k >= 3:
                fewer = model.addVar(vtype=GRB.BINARY, name=f"fewer[{i},{j}]")
                more = model.addVar(vtype=GRB.BINARY, name=f"more[{i},{j}]")
                model.addConstr(fewer + more >= 1 - grid[i, j], name=f"not_born[{i},{j}]")
                model.addConstr((fewer == 1) >> (live <= 2))
                model.addConstr((more == 1) >> (live >= 4))

    # Dead cells just outside the grid must not be born. A cell just above or below the
    # grid has, inside the grid, only the three cells of the border row beside it; a cell
    # at a corner or at the end of a side has at most two, so it cannot have 3. The three
    # must not all be alive. The same holds for the cells just left and right of the grid.
    model.addConstrs((gp.quicksum(grid[0, c] for c in range(j - 1, j + 2)) <= 2
                      for j in range(1, m - 1)), name="top")
    model.addConstrs((gp.quicksum(grid[n - 1, c] for c in range(j - 1, j + 2)) <= 2
                      for j in range(1, m - 1)), name="bottom")
    model.addConstrs((gp.quicksum(grid[r, 0] for r in range(i - 1, i + 2)) <= 2
                      for i in range(1, n - 1)), name="left")
    model.addConstrs((gp.quicksum(grid[r, m - 1] for r in range(i - 1, i + 2)) <= 2
                      for i in range(1, n - 1)), name="right")

    # Maximise the number of live cells in the grid.
    model.setObjective(grid.sum(), GRB.MAXIMIZE)

    return model, {"grid": [[grid[i, j] for j in range(m)] for i in range(n)]}


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
