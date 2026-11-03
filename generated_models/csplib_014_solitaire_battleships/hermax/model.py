# csplib_014_solitaire_battleships: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_014_solitaire_battleships.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_014_solitaire_battleships.py csplib_014_solitaire_battleships.json
"""Solitaire battleships (CSPLib prob014).

A hidden fleet of straight ships (horizontal or vertical) is placed on a grid of
rows x cols squares. The fleet has fleet_counts[k] = [length, count] ships of each
length. No two ships may touch, not even diagonally. rowsum and colsum give how many
squares of each row and column are occupied by ships, and some squares are already
known (hints). Each square gets one code: water, a one-square submarine (CIRCLE), or
a ship part (LEFT, RIGHT, TOP, BOTTOM, MIDDLE). The model outputs the grid of codes.
"""

from hermax.model import Model


def create_model(instance):
    # The instance fields this model reads.
    R = instance["rows"]              # number of rows of the grid
    C = instance["cols"]              # number of columns of the grid
    rowsum = instance["rowsum"]       # rowsum[r]: squares of row r occupied by ships
    colsum = instance["colsum"]       # colsum[c]: squares of column c occupied by ships
    fleet = instance["fleet_counts"]  # [length, count]: how many ships of each length
    hints = instance["hints"]         # [row, col, code]: a square whose code is known (0-based)
    WATER = instance["WATER"]         # code of an empty square
    CIRCLE = instance["CIRCLE"]       # code of a one-square submarine
    LEFT = instance["LEFT"]           # code of the left end of a horizontal ship
    RIGHT = instance["RIGHT"]         # code of the right end of a horizontal ship
    TOP = instance["TOP"]             # code of the top end of a vertical ship
    BOTTOM = instance["BOTTOM"]       # code of the bottom end of a vertical ship
    MIDDLE = instance["MIDDLE"]       # code of a middle square of a ship with three or more squares
    max_code = max(WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE)  # largest square code, the upper bound of grid's domain

    # Every place a ship of each length in the fleet can lie: (length, its squares, the code of each square).
    placements = []
    for length, _count in fleet:
        if length == 1:
            # a submarine is one square; horizontal and vertical are the same placement
            for r in range(R):
                for c in range(C):
                    placements.append((length, [(r, c)], [CIRCLE]))
            continue
        # horizontal ships: left end, middle squares, right end
        for r in range(R):
            for c in range(C - length + 1):
                cells = [(r, c + j) for j in range(length)]
                codes = [LEFT] + [MIDDLE] * (length - 2) + [RIGHT]
                placements.append((length, cells, codes))
        # vertical ships: top end, middle squares, bottom end
        for r in range(R - length + 1):
            for c in range(C):
                cells = [(r + j, c) for j in range(length)]
                codes = [TOP] + [MIDDLE] * (length - 2) + [BOTTOM]
                placements.append((length, cells, codes))

    m = Model()

    # ship[i] is true when placement i is one of the ships of the fleet.
    ship = [m.bool() for _ in placements]

    # The fleet: exactly fleet_counts[k] ships of each length k.
    for length, count in fleet:
        m &= (sum(ship[i] for i in range(len(placements)) if placements[i][0] == length) == count)

    # occ[r][c] is 1 when a ship covers square (r, c), else 0.
    # occ is the 0/1 view of the grid (grid != WATER) that the row, column and touching constraints use.
    occ = m.int_matrix("occ", R, C, 0, 1)
    covering = {(r, c): [] for r in range(R) for c in range(C)}
    for i, (_length, cells, _codes) in enumerate(placements):
        for cell in cells:
            covering[cell].append(i)
    # A square is occupied exactly when the chosen ships covering it number one.
    # Since occ is 0 or 1, no two ships can share a square.
    for r in range(R):
        for c in range(C):
            m &= (occ[r][c] == sum(ship[i] for i in covering[(r, c)]))

    # Row and column counts of occupied squares.
    for r in range(R):
        m &= (sum(occ[r][c] for c in range(C)) == rowsum[r])
    for c in range(C):
        m &= (sum(occ[r][c] for r in range(R)) == colsum[c])

    # Ships do not touch, not even diagonally: a chosen ship leaves every square
    # next to it, diagonals included, free of other ships.
    free = {(r, c): (occ[r][c] == 0) for r in range(R) for c in range(C)}
    for i, (_length, cells, _codes) in enumerate(placements):
        own = set(cells)
        around = set()
        for (r, c) in cells:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    y = (r + dr, c + dc)
                    if 0 <= y[0] < R and 0 <= y[1] < C and y not in own:
                        around.add(y)
        for y in sorted(around):
            m &= (~ship[i]) | free[y]

    # grid[r][c] is the code of square (r, c).
    grid = m.int_matrix("grid", R, C, 0, max_code)
    for r in range(R):
        for c in range(C):
            # a square no ship covers is water
            m &= (occ[r][c] == 1) | (grid[r][c] == WATER)
    # a chosen ship gives each of its squares the matching ship-part code
    for i, (_length, cells, codes) in enumerate(placements):
        for (r, c), code in zip(cells, codes):
            m &= (~ship[i]) | (grid[r][c] == code)

    # Shots given in the instance: these squares already show the given code.
    for r, c, code in hints:
        m &= (grid[r][c] == code)

    return m, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
