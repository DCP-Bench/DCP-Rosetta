# csplib_014_solitaire_battleships: a CPMpy model from DCP Rosetta.
# Download the `csplib_014_solitaire_battleships.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_014_solitaire_battleships.py csplib_014_solitaire_battleships.json

import cpmpy as cp


def create_model(instance):
    """Solitaire Battleships: fill a grid with water and ship parts so that the fleet of
    battleships, cruisers, destroyers and submarines is complete, no two ships occupy
    adjacent squares (not even diagonally), the row and column counts of ship squares are
    met, and the given shots hold."""
    rows = instance["rows"]        # the number of grid rows
    cols = instance["cols"]        # the number of grid columns
    rowsum = instance["rowsum"]    # rowsum[i]: the number of ship squares in row i
    colsum = instance["colsum"]    # colsum[j]: the number of ship squares in column j
    # fleet_counts lists [ship size, how many ships of that size]
    fleet_counts = {size: count for size, count in instance["fleet_counts"]}
    hints = instance["hints"]      # the shots taken: [row, column, cell value] triples

    # The cell values of the grid
    WATER = instance["WATER"]
    CIRCLE = instance["CIRCLE"]    # a submarine, a ship of one square
    LEFT = instance["LEFT"]        # the left end of a horizontal ship
    RIGHT = instance["RIGHT"]      # the right end of a horizontal ship
    TOP = instance["TOP"]          # the top end of a vertical ship
    BOTTOM = instance["BOTTOM"]    # the bottom end of a vertical ship
    MIDDLE = instance["MIDDLE"]    # an inner square of a ship of three or more squares

    # grid[r, c] is what the square in row r and column c holds: water or a ship part
    kinds = [WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE]
    grid = cp.intvar(min(kinds), max(kinds), shape=(rows, cols), name="grid")

    def one_of(r, c, kinds):
        """Condition: square (r, c) holds one of `kinds`. Squares outside the grid count as water."""
        if not (0 <= r < rows and 0 <= c < cols):
            return WATER in kinds
        return cp.any([grid[r, c] == k for k in kinds])

    def water(r, c):
        """Condition: square (r, c) is water (or outside the grid)."""
        return one_of(r, c, [WATER])

    model = cp.Model()

    # The shots show the content of some squares.
    for r, c, v in hints:
        model.add(grid[r, c] == v)

    # Each row and column holds the given number of ship squares (every non-water square).
    for i in range(rows):
        model.add(cp.sum(grid[i, :] > WATER) == rowsum[i])
    for j in range(cols):
        model.add(cp.sum(grid[:, j] > WATER) == colsum[j])

    # Ships are well formed and do not touch: each kind of square has the neighbours it needs.
    for r in range(rows):
        for c in range(cols):
            # Ships do not touch diagonally: the four diagonal neighbours of a ship square are water.
            diagonals = [water(r + dr, c + dc) for dr in (-1, 1) for dc in (-1, 1)]
            model.add((grid[r, c] > WATER).implies(cp.all(diagonals)))

            # A submarine is surrounded by water on all four sides.
            model.add((grid[r, c] == CIRCLE).implies(
                cp.all([water(r - 1, c), water(r + 1, c), water(r, c - 1), water(r, c + 1)])))

            # The left end of a ship continues to the right (middle or right end); the other
            # three neighbours are water.
            model.add((grid[r, c] == LEFT).implies(cp.all([
                one_of(r, c + 1, [MIDDLE, RIGHT]),
                water(r, c - 1), water(r - 1, c), water(r + 1, c)])))

            # The right end of a ship continues to the left (middle or left end).
            model.add((grid[r, c] == RIGHT).implies(cp.all([
                one_of(r, c - 1, [MIDDLE, LEFT]),
                water(r, c + 1), water(r - 1, c), water(r + 1, c)])))

            # The top end of a ship continues downward (middle or bottom end).
            model.add((grid[r, c] == TOP).implies(cp.all([
                one_of(r + 1, c, [MIDDLE, BOTTOM]),
                water(r - 1, c), water(r, c - 1), water(r, c + 1)])))

            # The bottom end of a ship continues upward (middle or top end).
            model.add((grid[r, c] == BOTTOM).implies(cp.all([
                one_of(r - 1, c, [MIDDLE, TOP]),
                water(r + 1, c), water(r, c - 1), water(r, c + 1)])))

            # A middle square lies inside a ship that is either horizontal or vertical.
            horizontal = cp.all([one_of(r, c - 1, [LEFT, MIDDLE]), one_of(r, c + 1, [RIGHT, MIDDLE]),
                                 water(r - 1, c), water(r + 1, c)])
            vertical = cp.all([one_of(r - 1, c, [TOP, MIDDLE]), one_of(r + 1, c, [BOTTOM, MIDDLE]),
                               water(r, c - 1), water(r, c + 1)])
            model.add((grid[r, c] == MIDDLE).implies(horizontal | vertical))

    # The fleet has the given number of ships of each size. Submarines (size 1) are counted directly.
    model.add(cp.sum(grid == CIRCLE) == fleet_counts[1])

    # A ship of size n is an end square, n-2 middle squares and the opposite end square in a
    # line (the rules above make every run of ship squares one such ship). Count the windows
    # of each size that read left-middle...-right or top-middle...-bottom.
    for size, count in fleet_counts.items():
        if size < 2:
            continue
        ships = []
        for r in range(rows):
            for c in range(cols - size + 1):
                ships.append(cp.all([grid[r, c] == LEFT, grid[r, c + size - 1] == RIGHT]
                                    + [grid[r, c + k] == MIDDLE for k in range(1, size - 1)]))
        for r in range(rows - size + 1):
            for c in range(cols):
                ships.append(cp.all([grid[r, c] == TOP, grid[r + size - 1, c] == BOTTOM]
                                    + [grid[r + k, c] == MIDDLE for k in range(1, size - 1)]))
        model.add(cp.sum(ships) == count)

    # There is no ship of a size outside the fleet: every left or top end starts one of the
    # ships counted above, so the number of such ends equals the number of ships longer than 1.
    model.add(cp.sum(grid == LEFT) + cp.sum(grid == TOP) == sum(
        count for size, count in fleet_counts.items() if size > 1))

    return model, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
