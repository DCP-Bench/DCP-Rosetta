"""Solitaire battleships: place the fleet on the grid to match the row and column counts and the given shots."""
import hexaly.optimizer as hx


def build(instance):
    rows, cols = instance["rows"], instance["cols"]
    rowsum, colsum, hints = instance["rowsum"], instance["colsum"], instance["hints"]
    WATER, SHIP, CIRCLE = instance["WATER"], instance["_SHIP"], instance["CIRCLE"]
    LEFT, RIGHT, TOP, BOTTOM, MIDDLE = (instance[k] for k in ("LEFT", "RIGHT", "TOP", "BOTTOM", "MIDDLE"))
    fleet = instance["fleet_counts"]  # (ship length, number of such ships)
    parts = [CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # is_part[i][j][k] = 1 if square (i, j) shows parts[k]; none set means water
    is_part = [[[model.bool() for _ in parts] for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            model.constraint(model.sum(is_part[i][j]) <= 1)

    def shows(i, j, *codes):
        """1 if square (i, j) shows one of the codes; squares off the grid show water."""
        if not (0 <= i < rows and 0 <= j < cols):
            return 1 if WATER in codes else 0
        found = model.sum(is_part[i][j][parts.index(c)] for c in codes if c != WATER)
        return 1 - model.sum(is_part[i][j]) + found if WATER in codes else found

    occupied = [[model.sum(is_part[i][j]) for j in range(cols)] for i in range(rows)]
    for i in range(rows):
        for j in range(cols):
            # No ship touches another, not even diagonally: the diagonal neighbours of a ship square are water
            for di, dj in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                model.constraint(occupied[i][j] <= shows(i + di, j + dj, WATER))
            # A submarine has water on all four sides
            for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                model.constraint(shows(i, j, CIRCLE) <= shows(i + di, j + dj, WATER))
            # The left end of a ship continues to the right, with water above, below and left of it
            model.constraint(shows(i, j, LEFT) <= shows(i, j + 1, MIDDLE, RIGHT))
            # The right end continues to the left
            model.constraint(shows(i, j, RIGHT) <= shows(i, j - 1, MIDDLE, LEFT))
            # The top end continues downwards, the bottom end upwards
            model.constraint(shows(i, j, TOP) <= shows(i + 1, j, MIDDLE, BOTTOM))
            model.constraint(shows(i, j, BOTTOM) <= shows(i - 1, j, MIDDLE, TOP))
            # Across a ship lying along a row is water; so is the far side of each end
            for code, sides in ((LEFT, ((-1, 0), (1, 0), (0, -1))), (RIGHT, ((-1, 0), (1, 0), (0, 1))),
                                (TOP, ((0, -1), (0, 1), (-1, 0))), (BOTTOM, ((0, -1), (0, 1), (1, 0)))):
                for di, dj in sides:
                    model.constraint(shows(i, j, code) <= shows(i + di, j + dj, WATER))
            # A middle part lies either between two parts of a row ship or between two parts of a column ship
            row_ship = model.and_(shows(i, j - 1, LEFT, MIDDLE) == 1, shows(i, j + 1, MIDDLE, RIGHT) == 1)
            col_ship = model.and_(shows(i - 1, j, TOP, MIDDLE) == 1, shows(i + 1, j, MIDDLE, BOTTOM) == 1)
            model.constraint(shows(i, j, MIDDLE) <= model.or_(row_ship, col_ship))

    # The number of ships of each length: submarines are circles; a longer ship has its left end
    # with L - 2 middles and a right end along the row, or the same downwards from a top end
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

    for size, count in fleet:
        model.constraint(ships_of(size) == count)
    # Every ship square belongs to a counted ship
    model.constraint(model.sum(occupied[i][j] for i in range(rows) for j in range(cols))
                     == sum(size * count for size, count in fleet))

    # The numbers of occupied squares in each row and column
    for i in range(rows):
        model.constraint(model.sum(occupied[i]) == rowsum[i])
    for j in range(cols):
        model.constraint(model.sum(occupied[i][j] for i in range(rows)) == colsum[j])
    # The shots already taken: water, a given part, or a ship of unknown part
    for i, j, code in hints:
        model.constraint(occupied[i][j] == 1 if code == SHIP else shows(i, j, code) == 1)

    # The code of every square: water or the part it shows
    grid = [[model.sum(parts[k] * is_part[i][j][k] for k in range(len(parts))) + WATER * (1 - occupied[i][j])
             for j in range(cols)] for i in range(rows)]
    return optimizer, {"grid": grid}
