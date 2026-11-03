# csplib_014_solitaire_battleships: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_014_solitaire_battleships.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_014_solitaire_battleships.py csplib_014_solitaire_battleships.json

from exact import Exact


def create_model(instance):
    """Solitaire battleships. Fill the grid with water, submarines and ship parts so that
    the fleet has the listed ships, every ship is straight, and no two ships touch, not even
    diagonally. Each row and column has the stated number of ship squares, and the shots
    already taken are shown."""
    rows = instance["rows"]          # the number of rows
    cols = instance["cols"]          # the number of columns
    rowsum = instance["rowsum"]      # rowsum[r]: the number of ship squares in row r
    colsum = instance["colsum"]      # colsum[c]: the number of ship squares in column c
    fleet = {size: count for size, count in instance["fleet_counts"]}  # fleet[size]: the number of ships that long
    hints = instance["hints"]        # (row, column, code) of each square that the shots show
    # code[k] is the number the instance uses for a square of kind k
    code = {"water": instance["WATER"], "circle": instance["CIRCLE"], "left": instance["LEFT"],
            "right": instance["RIGHT"], "top": instance["TOP"], "bottom": instance["BOTTOM"],
            "middle": instance["MIDDLE"]}
    # the kinds of square: water, a submarine, or one of the five ship parts
    kinds = list(code)
    # steps[d] is the change of (row, column) when moving in direction d
    steps = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
    # shown[(r, c)] is the code that the shots reveal for square (r, c)
    shown = {(r, c): value for r, c, value in hints}

    solver = Exact()

    # Exact identifies its variables by name.
    # grid[r][c] is the code of the square in row r and column c
    grid = [[f"grid_{r}_{c}" for c in range(cols)] for r in range(rows)]
    # is_kind[r][c][k] is 1 when the square in row r and column c is of kind k, and 0 when not
    is_kind = [[{k: f"cell_{r}_{c}_{k}" for k in kinds} for c in range(cols)] for r in range(rows)]
    for r in range(rows):
        for c in range(cols):
            solver.addVariable(grid[r][c], min(code.values()), max(code.values()))
            for k in kinds:
                # a square that the shots show is of the kind its shot reveals
                if (r, c) in shown:
                    lo = hi = int(code[k] == shown[(r, c)])
                else:
                    lo, hi = 0, 1
                solver.addVariable(is_kind[r][c][k], lo, hi)

    def neighbour(r, c, direction):
        """The square next to (r, c) in that direction, or None when it lies off the grid."""
        nr, nc = r + steps[direction][0], c + steps[direction][1]
        return (nr, nc) if 0 <= nr < rows and 0 <= nc < cols else None

    def water(r, c):
        """The variable that is 1 when square (r, c) is water."""
        return is_kind[r][c]["water"]

    def needs_one_of(head, alternatives):
        """If `head` is 1, one of the variables in `alternatives` is 1. With no alternatives, `head` is 0."""
        solver.addConstraint([(1, head)] + [(-1, a) for a in alternatives], False, 0, True, 0)

    def needs_kind_next_door(head, r, c, direction, allowed):
        """If `head` is 1, the square next door in that direction exists and is of an allowed kind."""
        nb = neighbour(r, c, direction)
        needs_one_of(head, [is_kind[nb[0]][nb[1]][k] for k in allowed] if nb else [])

    def needs_water_next_door(head, r, c, directions):
        """If `head` is 1, the squares next door in these directions are water. Off the grid, nothing is required."""
        for direction in directions:
            nb = neighbour(r, c, direction)
            if nb:
                needs_one_of(head, [water(*nb)])

    # Every square is of exactly one kind, and its code is the code of that kind.
    for r in range(rows):
        for c in range(cols):
            solver.addConstraint([(1, is_kind[r][c][k]) for k in kinds], True, 1, True, 1)
            solver.addConstraint([(code[k], is_kind[r][c][k]) for k in kinds if code[k]] + [(-1, grid[r][c])],
                                 True, 0, True, 0)

    # Each row and column has the stated number of ship squares, so the rest of it is water.
    for r in range(rows):
        solver.addConstraint([(1, water(r, c)) for c in range(cols)], True, cols - rowsum[r], True, cols - rowsum[r])
    for c in range(cols):
        solver.addConstraint([(1, water(r, c)) for r in range(rows)], True, rows - colsum[c], True, rows - colsum[c])

    # Ships do not touch, not even diagonally: of two diagonal neighbours at least one is water.
    # Each diagonal pair is covered once, from the upper square.
    for r in range(rows - 1):
        for c in range(cols):
            for dc in (-1, 1):
                if 0 <= c + dc < cols:
                    solver.addConstraint([(1, water(r, c)), (1, water(r + 1, c + dc))], True, 1)

    for r in range(rows):
        for c in range(cols):
            cell = is_kind[r][c]

            # A submarine has water on all four sides.
            needs_water_next_door(cell["circle"], r, c, list(steps))

            # A left end has the rest of its ship on the right, and water on its other three sides.
            needs_kind_next_door(cell["left"], r, c, "right", ("middle", "right"))
            needs_water_next_door(cell["left"], r, c, ("left", "up", "down"))

            # A right end has the rest of its ship on the left, and water on its other three sides.
            needs_kind_next_door(cell["right"], r, c, "left", ("middle", "left"))
            needs_water_next_door(cell["right"], r, c, ("right", "up", "down"))

            # A top end has the rest of its ship below it, and water on its other three sides.
            needs_kind_next_door(cell["top"], r, c, "down", ("middle", "bottom"))
            needs_water_next_door(cell["top"], r, c, ("up", "left", "right"))

            # A bottom end has the rest of its ship above it, and water on its other three sides.
            needs_kind_next_door(cell["bottom"], r, c, "up", ("middle", "top"))
            needs_water_next_door(cell["bottom"], r, c, ("down", "left", "right"))

            # A middle square lies in a horizontal ship or in a vertical one. Each way is a
            # variable that is 1 only when the squares around it fit that ship.
            ways = []
            for way, before, after, before_kinds, after_kinds, sides in (
                ("horizontal", "left", "right", ("left", "middle"), ("right", "middle"), ("up", "down")),
                ("vertical", "up", "down", ("top", "middle"), ("bottom", "middle"), ("left", "right")),
            ):
                if neighbour(r, c, before) and neighbour(r, c, after):
                    name = f"middle_{r}_{c}_{way}"
                    solver.addVariable(name, 0, 1)
                    needs_kind_next_door(name, r, c, before, before_kinds)
                    needs_kind_next_door(name, r, c, after, after_kinds)
                    needs_water_next_door(name, r, c, sides)
                    ways.append(name)
            needs_one_of(cell["middle"], ways)

    # The fleet has fleet[1] submarines.
    solver.addConstraint([(1, is_kind[r][c]["circle"]) for r in range(rows) for c in range(cols)],
                         True, fleet[1], True, fleet[1])

    # A ship of length n is a left end, n - 2 middle squares and a right end in a row, or a top
    # end, middle squares and a bottom end in a column. Each place a ship of length n can lie is
    # a variable, and it is 1 exactly when the squares there have those kinds.
    for size, count in fleet.items():
        if size < 2:
            continue
        placements = []  # (variable, squares that must have the kinds of the ship) for each place
        for r in range(rows):
            for c in range(cols - size + 1):
                needed = [is_kind[r][c]["left"]] + [is_kind[r][c + k]["middle"] for k in range(1, size - 1)] \
                    + [is_kind[r][c + size - 1]["right"]]
                placements.append((f"ship{size}_horizontal_{r}_{c}", needed))
        for r in range(rows - size + 1):
            for c in range(cols):
                needed = [is_kind[r][c]["top"]] + [is_kind[r + k][c]["middle"] for k in range(1, size - 1)] \
                    + [is_kind[r + size - 1][c]["bottom"]]
                placements.append((f"ship{size}_vertical_{r}_{c}", needed))
        for name, needed in placements:
            solver.addVariable(name, 0, 1)
            solver.addReification(name, True, [(1, v) for v in needed], size)
        # The fleet has count ships of this length.
        solver.addConstraint([(1, name) for name, _ in placements], True, count, True, count)

    long_ships = sum(count for size, count in fleet.items() if size > 1)  # the ships of two or more squares
    # Every left end and top end starts one of those ships, so no ship has any other length.
    solver.addConstraint([(1, is_kind[r][c][k]) for r in range(rows) for c in range(cols) for k in ("left", "top")],
                         True, long_ships, True, long_ships)

    return solver, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
