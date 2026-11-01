# csplib_014_solitaire_battleships: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_014_solitaire_battleships.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_014_solitaire_battleships.py csplib_014_solitaire_battleships.json

from pychoco.model import Model


def create_model(instance):
    """Solitaire battleships: fill the grid with water and ship parts so that the fleet of
    battleships, cruisers, destroyers and submarines is complete, no two ships touch (not
    even diagonally), every row and column holds the given number of ship squares, and the
    shots taken at the start hold."""
    rows = instance["rows"]          # the number of rows
    cols = instance["cols"]          # the number of columns
    rowsum = instance["rowsum"]      # rowsum[r]: the number of ship squares in row r
    colsum = instance["colsum"]      # colsum[c]: the number of ship squares in column c
    fleet_counts = {size: count for size, count in instance["fleet_counts"]}  # fleet_counts[size]: the number of ships of that size
    hints = instance["hints"]        # the shots: [row, column, kind] fixes the kind of one square
    WATER = instance["WATER"]        # the kind of an empty square
    CIRCLE = instance["CIRCLE"]      # the kind of a submarine, a ship of one square
    LEFT = instance["LEFT"]          # the left end of a horizontal ship
    RIGHT = instance["RIGHT"]        # the right end of a horizontal ship
    TOP = instance["TOP"]            # the top end of a vertical ship
    BOTTOM = instance["BOTTOM"]      # the bottom end of a vertical ship
    MIDDLE = instance["MIDDLE"]      # a square in the middle of a ship

    # The kinds of square are numbered 0 up to the largest kind.
    n_kinds = max(WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE) + 1

    model = Model()

    # grid[r][c] is the kind of the square in row r, column c
    grid = [[model.intvar(0, n_kinds - 1, name=f"grid_{r}_{c}") for c in range(cols)] for r in range(rows)]

    # is_code[r][c][k] is true when square (r, c) is of kind k. Each one is tied to the
    # grid square, so the rules below can speak about kinds.
    is_code = []
    for r in range(rows):
        row_flags = []
        for c in range(cols):
            flags = [model.boolvar(name=f"is_{r}_{c}_{k}") for k in range(n_kinds)]
            model.bools_int_channeling(flags, grid[r][c]).post()
            row_flags.append(flags)
        is_code.append(row_flags)

    def cell_is(code, r, c):
        """True when the square in row r, column c is of kind `code`."""
        return is_code[r][c][code]

    def clause(positive, negative):
        """If every square in `negative` is true, then one square in `positive` is true."""
        if positive and negative:
            model.add_clauses(positive, negative)
        elif positive:
            model.sum(positive, ">=", 1).post()
        else:
            model.sum(negative, "<=", len(negative) - 1).post()

    def inside(r, c):
        """True when (r, c) is a square of the grid."""
        return 0 <= r < rows and 0 <= c < cols

    # The shots fix the kind of some squares.
    for r, c, code in hints:
        model.arithm(grid[r][c], "=", code).post()

    # Each row holds rowsum[r] ship squares, so the rest of the row is water (and the same for columns).
    for r in range(rows):
        model.sum([cell_is(WATER, r, c) for c in range(cols)], "=", cols - rowsum[r]).post()
    for c in range(cols):
        model.sum([cell_is(WATER, r, c) for r in range(rows)], "=", rows - colsum[c]).post()

    for r in range(rows):
        for c in range(cols):
            water = cell_is(WATER, r, c)

            # No two ships touch diagonally: of two diagonal squares, at least one is water.
            for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                if inside(r + dr, c + dc):
                    clause([water, cell_is(WATER, r + dr, c + dc)], [])

            # A submarine has water on all four sides.
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                if inside(r + dr, c + dc):
                    clause([cell_is(WATER, r + dr, c + dc)], [cell_is(CIRCLE, r, c)])

            # The left end of a horizontal ship has a middle square or the right end to its right,
            # water above, below and to its left, and is not in the last column.
            left = cell_is(LEFT, r, c)
            if c < cols - 1:
                clause([cell_is(MIDDLE, r, c + 1), cell_is(RIGHT, r, c + 1)], [left])
            else:
                clause([], [left])
            for dr, dc in ((-1, 0), (1, 0), (0, -1)):
                if inside(r + dr, c + dc):
                    clause([cell_is(WATER, r + dr, c + dc)], [left])

            # The right end of a horizontal ship has a middle square or the left end to its left,
            # water above, below and to its right, and is not in the first column.
            right = cell_is(RIGHT, r, c)
            if c > 0:
                clause([cell_is(MIDDLE, r, c - 1), cell_is(LEFT, r, c - 1)], [right])
            else:
                clause([], [right])
            for dr, dc in ((-1, 0), (1, 0), (0, 1)):
                if inside(r + dr, c + dc):
                    clause([cell_is(WATER, r + dr, c + dc)], [right])

            # The top end of a vertical ship has a middle square or the bottom end below it,
            # water above, to its left and to its right, and is not in the last row.
            top = cell_is(TOP, r, c)
            if r < rows - 1:
                clause([cell_is(MIDDLE, r + 1, c), cell_is(BOTTOM, r + 1, c)], [top])
            else:
                clause([], [top])
            for dr, dc in ((-1, 0), (0, -1), (0, 1)):
                if inside(r + dr, c + dc):
                    clause([cell_is(WATER, r + dr, c + dc)], [top])

            # The bottom end of a vertical ship has a middle square or the top end above it,
            # water below, to its left and to its right, and is not in the first row.
            bottom = cell_is(BOTTOM, r, c)
            if r > 0:
                clause([cell_is(MIDDLE, r - 1, c), cell_is(TOP, r - 1, c)], [bottom])
            else:
                clause([], [bottom])
            for dr, dc in ((1, 0), (0, -1), (0, 1)):
                if inside(r + dr, c + dc):
                    clause([cell_is(WATER, r + dr, c + dc)], [bottom])

            # A middle square lies in a horizontal ship (ship squares to its left and right,
            # water above and below) or a vertical one (ship squares above and below, water to
            # its left and right). The square on its left tells the two apart: if that square is
            # water, or there is none, the ship is vertical; otherwise it is horizontal.
            middle = cell_is(MIDDLE, r, c)
            if c > 0:
                left_water = cell_is(WATER, r, c - 1)
                horizontal_if = [left_water]
                vertical_if = [left_water]
            else:
                left_water = None
                horizontal_if = []
                vertical_if = []
            # horizontal ship
            if 0 < c < cols - 1:
                clause(horizontal_if + [cell_is(LEFT, r, c - 1), cell_is(MIDDLE, r, c - 1)], [middle])
                clause(horizontal_if + [cell_is(RIGHT, r, c + 1), cell_is(MIDDLE, r, c + 1)], [middle])
                if r > 0:
                    clause(horizontal_if + [cell_is(WATER, r - 1, c)], [middle])
                if r < rows - 1:
                    clause(horizontal_if + [cell_is(WATER, r + 1, c)], [middle])
            elif c > 0:
                # last column: a horizontal ship needs a square to the right, so this one is vertical
                clause([left_water], [middle])
            # vertical ship
            if 0 < r < rows - 1:
                clause([cell_is(TOP, r - 1, c), cell_is(MIDDLE, r - 1, c)], [middle] + vertical_if)
                clause([cell_is(BOTTOM, r + 1, c), cell_is(MIDDLE, r + 1, c)], [middle] + vertical_if)
                if c < cols - 1:
                    clause([cell_is(WATER, r, c + 1)], [middle] + vertical_if)
            else:
                # first or last row: a vertical ship needs a square above and below, so this one is horizontal
                clause([], [middle] + vertical_if)

    # There are fleet_counts[1] submarines.
    model.sum([cell_is(CIRCLE, r, c) for r in range(rows) for c in range(cols)], "=", fleet_counts[1]).post()

    for size, count in fleet_counts.items():
        if size < 2:
            continue
        # placements[k] is true when a ship of this size lies on the k-th place it could lie: an
        # end, size - 2 middle squares and the other end, across a row or down a column.
        placements = []
        for r in range(rows):
            for c in range(cols - size + 1):
                cells = [cell_is(LEFT, r, c), cell_is(RIGHT, r, c + size - 1)]
                cells += [cell_is(MIDDLE, r, c + k) for k in range(1, size - 1)]
                placements.append(model.sum(cells, ">=", len(cells)).reify())
        for r in range(rows - size + 1):
            for c in range(cols):
                cells = [cell_is(TOP, r, c), cell_is(BOTTOM, r + size - 1, c)]
                cells += [cell_is(MIDDLE, r + k, c) for k in range(1, size - 1)]
                placements.append(model.sum(cells, ">=", len(cells)).reify())
        # There are count ships of this size.
        model.sum(placements, "=", count).post()

    # ends holds every left and top end. Each ship longer than one square has exactly one of
    # them, so this count leaves no ship of a size outside the fleet.
    ends = [cell_is(LEFT, r, c) for r in range(rows) for c in range(cols)]
    ends += [cell_is(TOP, r, c) for r in range(rows) for c in range(cols)]
    model.sum(ends, "=", sum(count for size, count in fleet_counts.items() if size > 1)).post()

    return model, {"grid": grid}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
