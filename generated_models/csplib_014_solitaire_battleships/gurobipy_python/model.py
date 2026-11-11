# csplib_014_solitaire_battleships: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_014_solitaire_battleships.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_014_solitaire_battleships.py csplib_014_solitaire_battleships.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Solitaire battleships: place the fleet of ships on the grid so that no two ships touch, even diagonally, every row and column holds its clue number of ship cells, and each given cell shows its given piece."""
    rows = instance["rows"]          # the number of rows of the grid
    cols = instance["cols"]          # the number of columns of the grid
    rowsum = instance["rowsum"]      # rowsum[r]: the number of ship cells in row r (the clue at the right)
    colsum = instance["colsum"]      # colsum[c]: the number of ship cells in column c (the clue below)
    fleet = instance["fleet_counts"]  # fleet[k] = [size, count]: count ships, each size cells long
    hints = instance["hints"]        # hints[k] = [row, col, value]: a cell the puzzle shows, and what it holds
    # The codes for the cell kinds, as the instance gives them.
    WATER = instance["WATER"]        # the code of a water cell
    SHIP = instance["_SHIP"]         # the code of a hinted cell that holds a ship part, which part is not given
    CIRCLE = instance["CIRCLE"]      # the code of a submarine, a ship one cell long
    LEFT = instance["LEFT"]          # the code of the left end of a horizontal ship
    RIGHT = instance["RIGHT"]        # the code of the right end of a horizontal ship
    TOP = instance["TOP"]            # the code of the top end of a vertical ship
    BOTTOM = instance["BOTTOM"]      # the code of the bottom end of a vertical ship
    MIDDLE = instance["MIDDLE"]      # the code of a middle cell of a ship longer than two cells
    R, C = range(rows), range(cols)  # the row numbers and the column numbers

    model = gp.Model("solitaire_battleships")

    # place[size, way, r, c] is 1 when a ship of that size starts at cell (r, c). A horizontal ship
    # (way "h") covers (r, c) to (r, c + size - 1); a vertical one (way "v") covers (r, c) to
    # (r + size - 1, c). A submarine (size 1) has no direction, so it is always way "h" and one cell.
    keys = [(s, "h", r, c) for s, _ in fleet for r in R for c in range(cols - s + 1)]
    keys += [(s, "v", r, c) for s, _ in fleet if s > 1 for r in range(rows - s + 1) for c in C]
    place = model.addVars(keys, vtype=GRB.BINARY, name="place")

    # The fleet has exactly count ships of each size (place.sum(size, "*", "*", "*") adds the
    # placements of that size).
    model.addConstrs((place.sum(size, "*", "*", "*") == count for size, count in fleet), name="fleet")

    # roles[k][r, c] is 1 when cell (r, c) is the piece k: circle (a submarine), left and right (the
    # ends of a horizontal ship), top and bottom (the ends of a vertical ship), or middle (a cell
    # inside a longer ship). Each is written as a linear expression of the placements.
    roles = {k: {(r, c): gp.LinExpr() for r in R for c in C}
             for k in ("circle", "left", "right", "top", "bottom", "middle")}
    # covers[r, c] is 1 when a ship of any size covers cell (r, c).
    covers = {(r, c): gp.LinExpr() for r in R for c in C}
    # sides lists each pair of cells that share a side: a cell and the cell to its right, and a cell
    # and the cell below it.
    sides = [((r, c), (r, c + 1)) for r in R for c in range(cols - 1)]
    sides += [((r, c), (r + 1, c)) for r in range(rows - 1) for c in C]
    # same_ship[u, v] adds the placements of the ships that cover both cells of the side pair (u, v).
    same_ship = {pair: gp.LinExpr() for pair in sides}
    for (size, way, r, c), v in place.items():
        if size == 1:
            roles["circle"][r, c] += v
            covers[r, c] += v
        elif way == "h":
            roles["left"][r, c] += v
            roles["right"][r, c + size - 1] += v
            for k in range(size):
                covers[r, c + k] += v
                if 0 < k < size - 1:
                    roles["middle"][r, c + k] += v
                if k < size - 1:
                    same_ship[(r, c + k), (r, c + k + 1)] += v
        else:
            roles["top"][r, c] += v
            roles["bottom"][r + size - 1, c] += v
            for k in range(size):
                covers[r + k, c] += v
                if 0 < k < size - 1:
                    roles["middle"][r + k, c] += v
                if k < size - 1:
                    same_ship[(r + k, c), (r + k + 1, c)] += v

    # A cell holds at most one piece.
    model.addConstrs((covers[r, c] <= 1 for r in R for c in C), name="one_piece")

    # Each row and each column has as many ship cells as its clue.
    model.addConstrs((gp.quicksum(covers[r, c] for c in C) == rowsum[r] for r in R), name="rowsum")
    model.addConstrs((gp.quicksum(covers[r, c] for r in R) == colsum[c] for c in C), name="colsum")

    # Ships do not touch diagonally: of two cells that touch at a corner, at most one is covered.
    model.addConstrs((covers[r, c] + covers[r + 1, c2] <= 1
                      for r in range(rows - 1) for c in C for c2 in (c - 1, c + 1) if 0 <= c2 < cols),
                     name="corner")

    # Ships do not touch along a side unless they are one ship: if both cells of a side pair are
    # covered, a single ship covers both.
    model.addConstrs((covers[u] + covers[v] <= 1 + same_ship[u, v] for u, v in sides), name="side")

    # The grid: each cell is one linear expression. A water cell gives the water code, and a cell
    # holding a piece gives that piece's code.
    code = {"circle": CIRCLE, "left": LEFT, "right": RIGHT, "top": TOP, "bottom": BOTTOM, "middle": MIDDLE}
    grid = [[WATER * (1 - covers[r, c]) + gp.quicksum(code[k] * roles[k][r, c] for k in code)
             for c in C] for r in R]

    # Each hint fixes its cell: water means no ship, the _SHIP code means a ship cell of any part,
    # and a piece code means the cell is that piece.
    for r, c, value in hints:
        if value == WATER:
            model.addConstr(covers[r, c] == 0, name=f"hint[{r},{c}]")
        elif value == SHIP:
            model.addConstr(covers[r, c] == 1, name=f"hint[{r},{c}]")
        else:
            names = [k for k in code if code[k] == value]
            model.addConstr(gp.quicksum(roles[k][r, c] for k in names) == 1, name=f"hint[{r},{c}]")

    # grid is the picture of the solution, one row per row of the puzzle.
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
