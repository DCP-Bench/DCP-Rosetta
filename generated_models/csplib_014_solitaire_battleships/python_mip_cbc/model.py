# csplib_014_solitaire_battleships: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_014_solitaire_battleships.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_014_solitaire_battleships.py csplib_014_solitaire_battleships.json

import mip


def create_model(instance):
    """Solitaire Battleships: fill a grid with water and ship parts so that the fleet of
    battleships, cruisers, destroyers and submarines is complete, no two ships occupy
    adjacent squares (not even diagonally), the row and column counts of ship squares are
    met, and the given shots hold."""
    rows = instance["rows"]      # the number of grid rows
    cols = instance["cols"]      # the number of grid columns
    rowsum = instance["rowsum"]  # rowsum[r]: the number of ship squares in row r
    colsum = instance["colsum"]  # colsum[c]: the number of ship squares in column c
    fleet_counts = instance["fleet_counts"]  # [length, count] pairs: the number of ships of each length
    hints = instance["hints"]    # [row, column, value] triples: the shots, each showing one square

    WATER = instance["WATER"]    # the value of a square with no ship on it
    CIRCLE = instance["CIRCLE"]  # the value of a submarine, a ship of one square
    LEFT = instance["LEFT"]      # the value of the left end of a horizontal ship
    RIGHT = instance["RIGHT"]    # the value of the right end of a horizontal ship
    TOP = instance["TOP"]        # the value of the top end of a vertical ship
    BOTTOM = instance["BOTTOM"]  # the value of the bottom end of a vertical ship
    MIDDLE = instance["MIDDLE"]  # the value of a square inside a ship of three or more squares

    model = mip.Model(solver_name="CBC")

    # The square values of a ship of this length, from its first square to its last.
    def ship_codes(orient, length):
        if length == 1:
            return [CIRCLE]
        if orient == "h":
            return [LEFT] + [MIDDLE] * (length - 2) + [RIGHT]
        return [TOP] + [MIDDLE] * (length - 2) + [BOTTOM]

    # The squares around a square, diagonal ones included, that lie on the grid.
    def neighbours(cell):
        r, c = cell
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if (dr, dc) != (0, 0) and 0 <= nr < rows and 0 <= nc < cols:
                    yield (nr, nc)

    # A ship of each length lies in a straight line, horizontal or vertical, from a starting
    # square (r, c). A submarine is a single square. Each possible place for a ship gets a
    # variable that is 1 when the ship lies there.
    placements = []  # (length, cells, [(cell, value), ...], variable) for each possible place
    for length, _ in fleet_counts:
        for r in range(rows):
            for c in range(cols):
                if length == 1:
                    options = [("s", [(r, c)])]
                else:
                    options = []
                    if c + length <= cols:
                        options.append(("h", [(r, c + i) for i in range(length)]))
                    if r + length <= rows:
                        options.append(("v", [(r + i, c) for i in range(length)]))
                for orient, cells in options:
                    ship = model.add_var(name=f"ship_{length}_{r}_{c}_{orient}", var_type=mip.BINARY)
                    codes = ship_codes(orient, length)
                    placements.append((length, cells, list(zip(cells, codes)), ship))

    # covering[(r, c)]: the (value, placement) pairs of the ships that can cover square (r, c).
    covering = {(r, c): [] for r in range(rows) for c in range(cols)}
    for _, _, cell_codes, ship in placements:
        for cell, code in cell_codes:
            covering[cell].append((code, ship))

    # The fleet: each length has as many ships as fleet_counts says.
    for length, count in fleet_counts:
        model += mip.xsum(ship for ln, _, _, ship in placements if ln == length) == count

    # Ships do not overlap: each square is covered by at most one ship.
    for cell in covering:
        model += mip.xsum(ship for _, ship in covering[cell]) <= 1

    # Ships do not touch, not even diagonally: a square next to a ship is not part of any other ship.
    for _, cells, _, ship in placements:
        ring = set()  # the squares next to the ship, without the ship's own squares
        for cell in cells:
            ring.update(neighbours(cell))
        ring.difference_update(cells)
        for q in ring:
            model += mip.xsum(other for _, other in covering[q]) + ship <= 1

    # The value of each square: WATER when no ship covers it, otherwise the value of the ship part on it.
    max_value = max(WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE)  # the largest value a square can take
    grid = []      # grid[r][c]: the value of square (r, c)
    occupied = {}  # occupied[(r, c)]: 1 when a ship covers square (r, c)
    for r in range(rows):
        row = []
        for c in range(cols):
            value = model.add_var(name=f"cell_{r}_{c}", lb=0, ub=max_value, var_type=mip.INTEGER)
            model += value == WATER + mip.xsum((code - WATER) * ship for code, ship in covering[(r, c)])
            occupied[(r, c)] = mip.xsum(ship for _, ship in covering[(r, c)])
            row.append(value)
        grid.append(row)

    # Each row and column holds its stated number of ship squares.
    for r in range(rows):
        model += mip.xsum(occupied[(r, c)] for c in range(cols)) == rowsum[r]
    for c in range(cols):
        model += mip.xsum(occupied[(r, c)] for r in range(rows)) == colsum[c]

    # The shots show the content of some squares.
    for r, c, code in hints:
        model += grid[r][c] == code

    return model, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
