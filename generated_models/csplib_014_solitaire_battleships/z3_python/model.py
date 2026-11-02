# csplib_014_solitaire_battleships: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_014_solitaire_battleships.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_014_solitaire_battleships.py csplib_014_solitaire_battleships.json

import z3


def create_model(instance):
    """Solitaire battleships: fill the grid with water and ships so that the fleet is complete,
    no two ships touch (not even at corners), and the row and column counts of ship squares
    match. Some squares are already known from shots taken."""
    rows = instance["rows"]            # the number of rows
    cols = instance["cols"]            # the number of columns
    rowsum = instance["rowsum"]        # rowsum[r]: the number of ship squares in row r
    colsum = instance["colsum"]        # colsum[c]: the number of ship squares in column c
    fleet = {size: count for size, count in instance["fleet_counts"]}  # fleet[s]: the number of ships of length s
    shots = instance["hints"]          # the shots taken: each shows what one square holds
    WATER = instance["WATER"]          # an empty square
    SHIP = instance["_SHIP"]           # the lowest code of a ship square
    CIRCLE = instance["CIRCLE"]        # a submarine, a ship of one square
    LEFT = instance["LEFT"]            # the left end of a horizontal ship
    RIGHT = instance["RIGHT"]          # the right end of a horizontal ship
    TOP = instance["TOP"]              # the top end of a vertical ship
    BOTTOM = instance["BOTTOM"]        # the bottom end of a vertical ship
    MIDDLE = instance["MIDDLE"]        # a square inside a ship of three or more squares

    # grid[r][c] is the content of the square in row r, column c: a code from the list above
    grid = [[z3.Int(f"grid_{r}_{c}") for c in range(cols)] for r in range(rows)]

    solver = z3.Solver()

    # Each square holds a code from water up to the middle of a ship.
    solver.add([grid[r][c] >= WATER for r in range(rows) for c in range(cols)])
    solver.add([grid[r][c] <= MIDDLE for r in range(rows) for c in range(cols)])

    # The square in row r, column c holds the given code.
    def cell(r, c, code):
        return grid[r][c] == code

    # The square in row r, column c is water.
    def water(r, c):
        return grid[r][c] == WATER

    # The square in row r, column c is part of a ship.
    def ship(r, c):
        return grid[r][c] >= SHIP

    # The shots already taken show the content of some squares.
    solver.add([grid[r][c] == v for r, c, v in shots])

    # Each row and column holds the stated number of ship squares.
    solver.add([z3.Sum([z3.If(ship(r, c), 1, 0) for c in range(cols)]) == rowsum[r]
                for r in range(rows)])
    solver.add([z3.Sum([z3.If(ship(r, c), 1, 0) for r in range(rows)]) == colsum[c]
                for c in range(cols)])

    for r in range(rows):
        for c in range(cols):
            # Ships do not touch, not even at corners: the four diagonal neighbours of a ship
            # square are water.
            diagonals = [water(r + dr, c + dc) for dr in (-1, 1) for dc in (-1, 1)
                         if 0 <= r + dr < rows and 0 <= c + dc < cols]
            solver.add(z3.Implies(ship(r, c), z3.And(diagonals)))

            # Squares off the grid count as water. A ship cannot run off the grid.
            above = water(r - 1, c) if r > 0 else z3.BoolVal(True)
            below = water(r + 1, c) if r < rows - 1 else z3.BoolVal(True)
            left_w = water(r, c - 1) if c > 0 else z3.BoolVal(True)
            right_w = water(r, c + 1) if c < cols - 1 else z3.BoolVal(True)

            # A submarine is surrounded by water on all four sides.
            solver.add(z3.Implies(cell(r, c, CIRCLE), z3.And(above, below, left_w, right_w)))

            # The left end of a horizontal ship continues to the right with a middle or right
            # square, and water lies on its other three sides.
            next_right = (z3.Or(cell(r, c + 1, MIDDLE), cell(r, c + 1, RIGHT))
                          if c < cols - 1 else z3.BoolVal(False))
            solver.add(z3.Implies(cell(r, c, LEFT), z3.And(next_right, left_w, above, below)))

            # The right end of a horizontal ship continues to the left with a middle or left square.
            prev_left = (z3.Or(cell(r, c - 1, MIDDLE), cell(r, c - 1, LEFT))
                         if c > 0 else z3.BoolVal(False))
            solver.add(z3.Implies(cell(r, c, RIGHT), z3.And(prev_left, right_w, above, below)))

            # The top end of a vertical ship continues downwards with a middle or bottom square.
            next_down = (z3.Or(cell(r + 1, c, MIDDLE), cell(r + 1, c, BOTTOM))
                         if r < rows - 1 else z3.BoolVal(False))
            solver.add(z3.Implies(cell(r, c, TOP), z3.And(next_down, above, left_w, right_w)))

            # The bottom end of a vertical ship continues upwards with a middle or top square.
            prev_up = (z3.Or(cell(r - 1, c, MIDDLE), cell(r - 1, c, TOP))
                       if r > 0 else z3.BoolVal(False))
            solver.add(z3.Implies(cell(r, c, BOTTOM), z3.And(prev_up, below, left_w, right_w)))

            # A middle square lies inside a horizontal ship (ship squares to its left and right,
            # water above and below) or inside a vertical ship.
            if 0 < c < cols - 1:
                horizontal = z3.And(z3.Or(cell(r, c - 1, LEFT), cell(r, c - 1, MIDDLE)),
                                    z3.Or(cell(r, c + 1, RIGHT), cell(r, c + 1, MIDDLE)),
                                    above, below)
            else:
                horizontal = z3.BoolVal(False)
            if 0 < r < rows - 1:
                vertical = z3.And(z3.Or(cell(r - 1, c, TOP), cell(r - 1, c, MIDDLE)),
                                  z3.Or(cell(r + 1, c, BOTTOM), cell(r + 1, c, MIDDLE)),
                                  left_w, right_w)
            else:
                vertical = z3.BoolVal(False)
            solver.add(z3.Implies(cell(r, c, MIDDLE), z3.Or(horizontal, vertical)))

    # The fleet has the stated number of submarines.
    solver.add(z3.Sum([z3.If(cell(r, c, CIRCLE), 1, 0)
                       for r in range(rows) for c in range(cols)]) == fleet[1])

    # For each longer ship length, the ships of exactly that length number as the fleet
    # states. A ship of length s is an end square, s - 2 middle squares and the other end,
    # in one line.
    for size, count in fleet.items():
        if size < 2:
            continue
        # ships: the places in the grid where a ship of this length can lie
        ships = []
        for r in range(rows):
            for c in range(cols - size + 1):
                ships.append(z3.And([cell(r, c, LEFT), cell(r, c + size - 1, RIGHT)]
                                    + [cell(r, c + k, MIDDLE) for k in range(1, size - 1)]))
        for r in range(rows - size + 1):
            for c in range(cols):
                ships.append(z3.And([cell(r, c, TOP), cell(r + size - 1, c, BOTTOM)]
                                    + [cell(r + k, c, MIDDLE) for k in range(1, size - 1)]))
        solver.add(z3.Sum([z3.If(s, 1, 0) for s in ships]) == count)

    # ends: one for each square that is the left or top end of a ship. Every such end starts
    # one of the ships counted above, so the ends match the ships longer than one square.
    ends = [z3.If(z3.Or(cell(r, c, LEFT), cell(r, c, TOP)), 1, 0)
            for r in range(rows) for c in range(cols)]
    solver.add(z3.Sum(ends) == sum(count for size, count in fleet.items() if size > 1))

    return solver, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
