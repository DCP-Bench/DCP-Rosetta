# csplib_014_solitaire_battleships: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_014_solitaire_battleships.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_014_solitaire_battleships.py csplib_014_solitaire_battleships.json

from pyscipopt import Model, quicksum
import numpy as np


def create_model(instance):
    """Solitaire battleships: place a fleet of straight ships on a rectangular grid.

    Each ship is a straight line of squares, and the fleet has the number of ships of
    each length that the instance gives. No two ships touch, not even diagonally. Each
    row and each column has as many ship squares as its clue says, and each hinted
    square holds its given code. Every square holds one code: water, a submarine, or
    one part of a ship (left, right, top, bottom or middle). The answer is the grid of
    those codes.
    """
    rows = instance["rows"]           # the number of rows of the grid
    cols = instance["cols"]           # the number of columns of the grid
    rowsum = instance["rowsum"]       # rowsum[r]: the number of ship squares in row r
    colsum = instance["colsum"]       # colsum[c]: the number of ship squares in column c
    fleet = instance["fleet_counts"]  # fleet[i] = [length, count]: count ships of that length
    hints = instance["hints"]         # hints[i] = [row, col, code]: square (row, col) holds code, counted from 0
    WATER = instance["WATER"]         # the code of an empty square
    CIRCLE = instance["CIRCLE"]       # the code of a submarine, a ship of length 1
    LEFT = instance["LEFT"]           # the code of the left end of a horizontal ship
    RIGHT = instance["RIGHT"]         # the code of the right end of a horizontal ship
    TOP = instance["TOP"]             # the code of the top end of a vertical ship
    BOTTOM = instance["BOTTOM"]       # the code of the bottom end of a vertical ship
    MIDDLE = instance["MIDDLE"]       # the code of a square inside a ship, between its ends

    model = Model("csplib_014_solitaire_battleships")

    # water[r, c] is 1 when square (r, c) is water, and 0 when a ship covers it
    water = model.addMatrixVar((rows, cols), vtype="B", name="water")

    # parts[r, c] lists (code, ship) for every candidate ship that could cover square (r, c),
    # where code is the part of that ship the square would be
    parts = {(r, c): [] for r in range(rows) for c in range(cols)}

    # Ship lengths cannot be counted from the squares alone, so each candidate ship is a
    # variable: a straight line of the given length that fits on the grid. The fleet
    # counts the candidates of each length that are placed.
    for length, count in fleet:
        placed = []  # the candidate ships of this length
        # a submarine has no direction, so it is a candidate once
        for horizontal in ((True,) if length == 1 else (True, False)):
            for r in range(rows):
                for c in range(cols):
                    # the squares the candidate covers, from its first square to its last
                    if horizontal:
                        cells = [(r, c + k) for k in range(length)]
                    else:
                        cells = [(r + k, c) for k in range(length)]
                    if any(pr >= rows or pc >= cols for pr, pc in cells):
                        continue  # the ship would run off the grid

                    # ship is 1 when this candidate ship is placed, and 0 when it is not
                    ship = model.addVar(vtype="B", name=f"ship{length}_{r}_{c}_{'across' if horizontal else 'down'}")
                    placed.append(ship)

                    for k, (pr, pc) in enumerate(cells):
                        if length == 1:
                            code = CIRCLE
                        elif k == 0:
                            code = LEFT if horizontal else TOP
                        elif k == length - 1:
                            code = RIGHT if horizontal else BOTTOM
                        else:
                            code = MIDDLE
                        parts[pr, pc].append((code, ship))

                    # a square next to this ship, even diagonally and not part of it, is water:
                    # if the ship is placed, water[v] >= ship forces water[v] to 1, so no two ships touch
                    touching = {(nr, nc) for pr, pc in cells
                                for nr in range(pr - 1, pr + 2) for nc in range(pc - 1, pc + 2)
                                if 0 <= nr < rows and 0 <= nc < cols} - set(cells)
                    for nr, nc in touching:
                        model.addCons(water[nr, nc] >= ship)

        # the fleet has exactly count ships of this length
        model.addCons(quicksum(placed) == count)

    # cover[r, c] is the sum of the candidate ships covering square (r, c)
    cover = np.array([[quicksum(ship for _, ship in parts[r, c]) for c in range(cols)]
                      for r in range(rows)], dtype=object)
    # every square is either water or covered by exactly one ship
    model.addMatrixCons(water + cover == 1)

    # the ship squares of each row and column (the squares that are not water) match the clues
    model.addMatrixCons((1 - water).sum(axis=1) == rowsum)
    model.addMatrixCons((1 - water).sum(axis=0) == colsum)

    # each hint fixes its square: it is water, or the one ship part with the hinted code
    for r, c, code in hints:
        if code == WATER:
            model.addCons(water[r, c] == 1)
        else:
            model.addCons(quicksum(ship for part_code, ship in parts[r, c] if part_code == code) == 1)

    # there is no objective: any grid that meets every rule above is an answer

    # grid[r][c] is the code of square (r, c): the water code, or the code of the ship part covering it
    grid = [[WATER * water[r, c] + quicksum(code * ship for code, ship in parts[r, c])
             for c in range(cols)] for r in range(rows)]

    return model, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
