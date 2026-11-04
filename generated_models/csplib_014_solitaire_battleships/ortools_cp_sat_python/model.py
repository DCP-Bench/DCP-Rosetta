# csplib_014_solitaire_battleships: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_014_solitaire_battleships.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_014_solitaire_battleships.py csplib_014_solitaire_battleships.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Solitaire Battleships: fill a grid with water and ship parts so that the fleet of
    battleships, cruisers, destroyers and submarines is complete, no two ships occupy
    adjacent squares (not even diagonally), the row and column counts of ship squares are
    met, and the given shots hold."""
    rows = instance["rows"]          # the number of grid rows
    cols = instance["cols"]          # the number of grid columns
    rowsum = instance["rowsum"]      # rowsum[r]: the number of ship squares in row r
    colsum = instance["colsum"]      # colsum[c]: the number of ship squares in column c
    fleet = instance["fleet_counts"]  # the fleet: how many ships there are of each size
    hints = instance["hints"]        # the shots already taken, each fixing the content of one square

    WATER, CIRCLE = instance["WATER"], instance["CIRCLE"]  # an empty square, a submarine
    LEFT, RIGHT = instance["LEFT"], instance["RIGHT"]      # left and right ends of a ship
    TOP, BOTTOM = instance["TOP"], instance["BOTTOM"]      # top and bottom ends of a ship
    MIDDLE = instance["MIDDLE"]                            # a square inside a ship

    model = cp_model.CpModel()

    # the kinds of square: water, a submarine, or one of the five ship parts
    codes = [WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE]
    # is_code[t][r][c] is true when square (r, c) holds code t
    is_code = {t: [[model.new_bool_var(f"is{t}_{r}_{c}") for c in range(cols)] for r in range(rows)]
               for t in codes}
    # grid[r][c] is the code of square (r, c)
    grid = [[model.new_int_var(0, max(codes), f"grid_{r}_{c}") for c in range(cols)] for r in range(rows)]

    # true when square (r, c) lies on the grid
    def inside(r, c):
        return 0 <= r < rows and 0 <= c < cols

    # true when square (r, c) holds a ship part or a submarine
    def occupied(r, c):
        return ~is_code[WATER][r][c]

    def require(cell, water_neighbours, one_of=None):
        """If `cell` holds, the listed neighbours are water, and the neighbour `one_of`
        holds one of its codes. A neighbour off the grid is water and holds no code."""
        for nr, nc in water_neighbours:
            if inside(nr, nc):
                model.add_implication(cell, is_code[WATER][nr][nc])
        if one_of is not None:
            (nr, nc), allowed = one_of
            if inside(nr, nc):
                model.add_bool_or([is_code[t][nr][nc] for t in allowed]).only_enforce_if(cell)
            else:
                model.add(cell == 0)  # the rest of the ship would lie off the grid

    # Each square holds exactly one code.
    for r in range(rows):
        for c in range(cols):
            model.add_exactly_one(is_code[t][r][c] for t in codes)
            model.add(grid[r][c] == sum(t * is_code[t][r][c] for t in codes))

    # The shots already taken fix the content of some squares.
    for r, c, value in hints:
        model.add(grid[r][c] == value)

    # Each row and column holds the stated number of ship squares.
    for r in range(rows):
        model.add(sum(occupied(r, c) for c in range(cols)) == rowsum[r])
    for c in range(cols):
        model.add(sum(occupied(r, c) for r in range(rows)) == colsum[c])

    for r in range(rows):
        for c in range(cols):
            # Ships do not touch, not even diagonally: the four diagonal neighbours of a ship
            # square are water.
            for nr, nc in [(r - 1, c - 1), (r - 1, c + 1), (r + 1, c - 1), (r + 1, c + 1)]:
                if inside(nr, nc):
                    model.add_implication(occupied(r, c), is_code[WATER][nr][nc])

            # A submarine is surrounded by water.
            require(is_code[CIRCLE][r][c], [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)])
            # The left end of a ship continues to the right, and the other three sides are water.
            require(is_code[LEFT][r][c], [(r, c - 1), (r - 1, c), (r + 1, c)],
                    one_of=((r, c + 1), [MIDDLE, RIGHT]))
            # The right end of a ship continues to the left.
            require(is_code[RIGHT][r][c], [(r, c + 1), (r - 1, c), (r + 1, c)],
                    one_of=((r, c - 1), [MIDDLE, LEFT]))
            # The top end of a ship continues downwards.
            require(is_code[TOP][r][c], [(r - 1, c), (r, c - 1), (r, c + 1)],
                    one_of=((r + 1, c), [MIDDLE, BOTTOM]))
            # The bottom end of a ship continues upwards.
            require(is_code[BOTTOM][r][c], [(r + 1, c), (r, c - 1), (r, c + 1)],
                    one_of=((r - 1, c), [MIDDLE, TOP]))

            # A middle square lies inside a horizontal ship (ship squares to its left and right,
            # water above and below) or a vertical one (the same turned a quarter).
            horizontal = model.new_bool_var(f"horizontal_{r}_{c}")
            vertical = model.new_bool_var(f"vertical_{r}_{c}")
            model.add_bool_or([horizontal, vertical]).only_enforce_if(is_code[MIDDLE][r][c])
            if inside(r, c - 1) and inside(r, c + 1):
                model.add_bool_or([is_code[LEFT][r][c - 1], is_code[MIDDLE][r][c - 1]]).only_enforce_if(horizontal)
                model.add_bool_or([is_code[RIGHT][r][c + 1], is_code[MIDDLE][r][c + 1]]).only_enforce_if(horizontal)
                for nr, nc in [(r - 1, c), (r + 1, c)]:
                    if inside(nr, nc):
                        model.add_implication(horizontal, is_code[WATER][nr][nc])
            else:
                model.add(horizontal == 0)
            if inside(r - 1, c) and inside(r + 1, c):
                model.add_bool_or([is_code[TOP][r - 1][c], is_code[MIDDLE][r - 1][c]]).only_enforce_if(vertical)
                model.add_bool_or([is_code[BOTTOM][r + 1][c], is_code[MIDDLE][r + 1][c]]).only_enforce_if(vertical)
                for nr, nc in [(r, c - 1), (r, c + 1)]:
                    if inside(nr, nc):
                        model.add_implication(vertical, is_code[WATER][nr][nc])
            else:
                model.add(vertical == 0)

    # The fleet has the stated number of ships of each size.
    n_ships = 0  # the number of ships longer than one square
    for size, count in fleet:
        if size == 1:
            # Submarines are single squares.
            model.add(sum(is_code[CIRCLE][r][c] for r in range(rows) for c in range(cols)) == count)
            continue
        n_ships += count
        # A ship of this size is an end, size - 2 middle squares and the other end, in a line.
        # placed: one flag for each place where such a ship can lie, true when the ship lies there.
        placed = []
        for r in range(rows):
            for c in range(cols - size + 1):
                # the squares of a horizontal ship of this size starting at (r, c)
                cells = [is_code[LEFT][r][c], is_code[RIGHT][r][c + size - 1]] + \
                        [is_code[MIDDLE][r][c + k] for k in range(1, size - 1)]
                ship = model.new_bool_var(f"ship_h_{size}_{r}_{c}")
                model.add_bool_and(cells).only_enforce_if(ship)
                model.add_bool_or([~x for x in cells]).only_enforce_if(~ship)
                placed.append(ship)
        for r in range(rows - size + 1):
            for c in range(cols):
                # the squares of a vertical ship of this size starting at (r, c)
                cells = [is_code[TOP][r][c], is_code[BOTTOM][r + size - 1][c]] + \
                        [is_code[MIDDLE][r + k][c] for k in range(1, size - 1)]
                ship = model.new_bool_var(f"ship_v_{size}_{r}_{c}")
                model.add_bool_and(cells).only_enforce_if(ship)
                model.add_bool_or([~x for x in cells]).only_enforce_if(~ship)
                placed.append(ship)
        model.add(sum(placed) == count)

    # Every left or top end starts one of the ships counted above, so no ship has a size
    # outside the fleet.
    model.add(
        sum(is_code[LEFT][r][c] + is_code[TOP][r][c] for r in range(rows) for c in range(cols)) == n_ships
    )

    return model, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
