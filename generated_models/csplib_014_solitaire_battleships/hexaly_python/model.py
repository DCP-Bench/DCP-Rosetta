"""Solitaire battleships: place the fleet on the grid to match the row and column counts and the given shots.
Ships lie along a row or a column and no two touch, not even diagonally. Each square of the grid is water,
a submarine, or a ship part (left, right, top, bottom, middle)."""
import hexaly.optimizer as hx


def build(instance):
    rows, cols = instance["rows"], instance["cols"]  # number of rows and of columns of the grid
    # rowsum[i], colsum[j]: number of squares occupied by ships in row i and in column j
    # hints[k] = (row, column, code): a shot already taken, with the code that square shows
    rowsum, colsum, hints = instance["rowsum"], instance["colsum"], instance["hints"]
    # Integer codes for what a square shows: WATER; CIRCLE is a submarine (a ship of length 1);
    # _SHIP is used only by hints, for a shot that hit a ship square without saying which part
    WATER, SHIP, CIRCLE = instance["WATER"], instance["_SHIP"], instance["CIRCLE"]
    # LEFT, RIGHT: the ends of a ship lying along a row; TOP, BOTTOM: the ends of a ship lying along a column;
    # MIDDLE: a part of a ship of length 3 or more that is not an end
    LEFT, RIGHT, TOP, BOTTOM, MIDDLE = (instance[k] for k in ("LEFT", "RIGHT", "TOP", "BOTTOM", "MIDDLE"))
    fleet = instance["fleet_counts"]  # fleet[k] = (ship length, number of ships of that length)
    parts = [CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE]  # every code a square can show except water
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # is_part[i][j][k] = 1 if the square in row i, column j shows parts[k]; none set means water
    is_part = [[[model.bool() for _ in parts] for _ in range(cols)] for _ in range(rows)]
    # A square shows at most one part
    for i in range(rows):
        for j in range(cols):
            model.constraint(model.sum(is_part[i][j]) <= 1)

    # shows(i, j, *codes) is 1 if square (i, j) shows one of the codes. Water is the absence of every part,
    # and squares off the grid are water, so ships at the border need no special case.
    def shows(i, j, *codes):
        """1 if square (i, j) shows one of the codes; squares off the grid show water."""
        if not (0 <= i < rows and 0 <= j < cols):
            return 1 if WATER in codes else 0
        found = model.sum(is_part[i][j][parts.index(c)] for c in codes if c != WATER)
        return 1 - model.sum(is_part[i][j]) + found if WATER in codes else found

    # occupied[i][j] = 1 if square (i, j) holds a ship part (a submarine, an end or a middle)
    occupied = [[model.sum(is_part[i][j]) for j in range(cols)] for i in range(rows)]
    for i in range(rows):
        for j in range(cols):
            # No ship touches another, not even diagonally: the diagonal neighbours of a ship square are water.
            # The orthogonal neighbours are settled by the rules for each part below.
            for di, dj in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                model.constraint(occupied[i][j] <= shows(i + di, j + dj, WATER))
            # A submarine has water on all four sides
            for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                model.constraint(shows(i, j, CIRCLE) <= shows(i + di, j + dj, WATER))
            # The left end of a ship continues to the right, with a middle or the right end next to it
            model.constraint(shows(i, j, LEFT) <= shows(i, j + 1, MIDDLE, RIGHT))
            # The right end continues to the left
            model.constraint(shows(i, j, RIGHT) <= shows(i, j - 1, MIDDLE, LEFT))
            # The top end continues downwards, the bottom end upwards
            model.constraint(shows(i, j, TOP) <= shows(i + 1, j, MIDDLE, BOTTOM))
            model.constraint(shows(i, j, BOTTOM) <= shows(i - 1, j, MIDDLE, TOP))
            # Each end has water across the ship and beyond the end: for a left end the squares above, below
            # and to its left, and the same turned to the right, top and bottom ends
            for code, sides in ((LEFT, ((-1, 0), (1, 0), (0, -1))), (RIGHT, ((-1, 0), (1, 0), (0, 1))),
                                (TOP, ((0, -1), (0, 1), (-1, 0))), (BOTTOM, ((0, -1), (0, 1), (1, 0)))):
                for di, dj in sides:
                    model.constraint(shows(i, j, code) <= shows(i + di, j + dj, WATER))
            # A middle part lies either between two parts of a row ship or between two parts of a column ship
            row_ship = model.and_(shows(i, j - 1, LEFT, MIDDLE) == 1, shows(i, j + 1, MIDDLE, RIGHT) == 1)
            col_ship = model.and_(shows(i - 1, j, TOP, MIDDLE) == 1, shows(i + 1, j, MIDDLE, BOTTOM) == 1)
            model.constraint(shows(i, j, MIDDLE) <= model.or_(row_ship, col_ship))

    # ships_of(size) counts the ships of that length: submarines are the circles; a longer ship is a left end,
    # size - 2 middles and a right end along a row, or the same downwards from a top end to a bottom end
    def ships_of(size):
        if size == 1:
            return model.sum(shows(i, j, CIRCLE) for i in range(rows) for j in range(cols))
        found = []
        for i in range(rows):
            for j in range(cols):
                if j + size <= cols:
                    found.append(model.and_(shows(i, j, LEFT) == 1, shows(i, j + size - 1, RIGHT) == 1,
                                            *[shows(i, j + k, MIDDLE) == 1 for k in range(1, size - 1)]))
                if i + size <= rows:
                    found.append(model.and_(shows(i, j, TOP) == 1, shows(i + size - 1, j, BOTTOM) == 1,
                                            *[shows(i + k, j, MIDDLE) == 1 for k in range(1, size - 1)]))
        return model.sum(found)

    # The fleet has exactly the given number of ships of each length
    for size, count in fleet:
        model.constraint(ships_of(size) == count)
    # Every ship square belongs to a counted ship: the occupied squares are exactly the squares of the whole fleet
    model.constraint(model.sum(occupied[i][j] for i in range(rows) for j in range(cols))
                     == sum(size * count for size, count in fleet))

    # The digits beside the grid: row i has rowsum[i] occupied squares and column j has colsum[j]
    for i in range(rows):
        model.constraint(model.sum(occupied[i]) == rowsum[i])
    for j in range(cols):
        model.constraint(model.sum(occupied[i][j] for i in range(rows)) == colsum[j])
    # The shots already taken: water, a given part, or a ship of unknown part
    for i, j, code in hints:
        model.constraint(occupied[i][j] == 1 if code == SHIP else shows(i, j, code) == 1)

    # grid[i][j] = code of the square in row i, column j: water or the part it shows (the output of the problem)
    grid = [[model.sum(parts[k] * is_part[i][j][k] for k in range(len(parts))) + WATER * (1 - occupied[i][j])
             for j in range(cols)] for i in range(rows)]
    return optimizer, {"grid": grid}
