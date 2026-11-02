# csplib_014_solitaire_battleships: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_014_solitaire_battleships.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_014_solitaire_battleships.py csplib_014_solitaire_battleships.json

import cvc5.pythonic as c5


def create_model(instance):
    """Solitaire battleships: fill a grid with water and ship parts so that the fleet of
    battleships, cruisers, destroyers and submarines is complete, no two ships touch, even
    diagonally, the row and column counts of ship squares are met, and the shots hold."""
    rows = instance["rows"]                  # the number of grid rows
    cols = instance["cols"]                  # the number of grid columns
    rowsum = instance["rowsum"]              # rowsum[r]: the number of ship squares in row r
    colsum = instance["colsum"]              # colsum[c]: the number of ship squares in column c
    fleet_counts = instance["fleet_counts"]  # [size, count] pairs: how many ships of each size
    hints = instance["hints"]                # [row, column, content]: a square shown from the start

    WATER = instance["WATER"]    # the content of a square with no ship
    CIRCLE = instance["CIRCLE"]  # the content of a submarine, a ship of one square
    LEFT = instance["LEFT"]      # the left end of a horizontal ship
    RIGHT = instance["RIGHT"]    # the right end of a horizontal ship
    TOP = instance["TOP"]        # the top end of a vertical ship
    BOTTOM = instance["BOTTOM"]  # the bottom end of a vertical ship
    MIDDLE = instance["MIDDLE"]  # a square inside a ship of three or more squares

    # grid[r][c] is the content of the square in row r and column c
    grid = [[c5.Int(f"grid_{r}_{c}") for c in range(cols)] for r in range(rows)]

    solver = c5.Solver()

    def inside(r, c):
        """True when the square (r, c) is on the grid."""
        return 0 <= r < rows and 0 <= c < cols

    def water_around(r, c, skip=()):
        """The squares around (r, c) that are water, except the offsets in skip, which
        belong to the same ship."""
        return [grid[r + dr][c + dc] == WATER
                for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                if (dr, dc) != (0, 0) and (dr, dc) not in skip and inside(r + dr, c + dc)]

    def ship_end(r, c, end, other_end, dr, dc):
        """Conditions for a ship end at (r, c) whose ship runs in direction (dr, dc)."""
        if not inside(r + dr, c + dc):
            return [grid[r][c] != end]
        nr, nc = r + dr, c + dc
        return [c5.Implies(grid[r][c] == end, w) for w in water_around(r, c, skip={(dr, dc)})] + [
            c5.Implies(grid[r][c] == end, c5.Or(grid[nr][nc] == other_end, grid[nr][nc] == MIDDLE))]

    # Every square holds water or one of the ship codes.
    for r in range(rows):
        for c in range(cols):
            solver.add(c5.Or([grid[r][c] == v for v in [WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE]]))

    for r in range(rows):
        for c in range(cols):
            cell = grid[r][c]

            # A submarine has water all around it, diagonals included.
            solver.add([c5.Implies(cell == CIRCLE, w) for w in water_around(r, c)])

            # Ship ends: the next square along the ship is the rest of it, and every other
            # square around an end is water, diagonals included.
            solver.add(ship_end(r, c, LEFT, RIGHT, 0, 1))
            solver.add(ship_end(r, c, RIGHT, LEFT, 0, -1))
            solver.add(ship_end(r, c, TOP, BOTTOM, 1, 0))
            solver.add(ship_end(r, c, BOTTOM, TOP, -1, 0))

            # A middle square lies in a horizontal ship (the squares to its left and right
            # continue it, the squares above and below are water) or in a vertical one.
            options = []
            if 0 < c < cols - 1:
                options.append(c5.And(
                    [c5.Or(grid[r][c - 1] == LEFT, grid[r][c - 1] == MIDDLE),
                     c5.Or(grid[r][c + 1] == RIGHT, grid[r][c + 1] == MIDDLE)]
                    + water_around(r, c, skip={(0, -1), (0, 1)})))
            if 0 < r < rows - 1:
                options.append(c5.And(
                    [c5.Or(grid[r - 1][c] == TOP, grid[r - 1][c] == MIDDLE),
                     c5.Or(grid[r + 1][c] == BOTTOM, grid[r + 1][c] == MIDDLE)]
                    + water_around(r, c, skip={(-1, 0), (1, 0)})))
            if not options:
                solver.add(cell != MIDDLE)
            else:
                solver.add(c5.Implies(
                    cell == MIDDLE, options[0] if len(options) == 1 else c5.Or(options)))

    # Every row and every column has its stated number of ship squares.
    for r in range(rows):
        solver.add(c5.Sum([c5.If(grid[r][c] != WATER, 1, 0) for c in range(cols)]) == rowsum[r])
    for c in range(cols):
        solver.add(c5.Sum([c5.If(grid[r][c] != WATER, 1, 0) for r in range(rows)]) == colsum[c])

    for length, count in fleet_counts:
        if length == 1:
            # The fleet has the stated number of submarines.
            solver.add(c5.Sum(
                [c5.If(grid[r][c] == CIRCLE, 1, 0) for r in range(rows) for c in range(cols)]) == count)
            continue
        # A ship of this length starts at its left or top end and runs for length squares,
        # with middle squares between the two ends. Each such placement counts once.
        starts = []
        for r in range(rows):
            for c in range(cols):
                if inside(r, c + length - 1):
                    starts.append(c5.If(c5.And(
                        [grid[r][c] == LEFT, grid[r][c + length - 1] == RIGHT]
                        + [grid[r][c + j] == MIDDLE for j in range(1, length - 1)]), 1, 0))
                if inside(r + length - 1, c):
                    starts.append(c5.If(c5.And(
                        [grid[r][c] == TOP, grid[r + length - 1][c] == BOTTOM]
                        + [grid[r + j][c] == MIDDLE for j in range(1, length - 1)]), 1, 0))
        # The fleet has the stated number of ships of this length.
        solver.add(c5.Sum(starts) == count)

    # The shots fix the content of the squares they show.
    for r, c, content in hints:
        solver.add(grid[r][c] == content)

    outputs = {"grid": grid}
    return solver, outputs


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
