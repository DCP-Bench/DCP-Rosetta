"""Solitaire battleships: place the fleet on the grid to match the row and column counts and the given shots."""
import hexaly.optimizer as hx


def build(instance):
    rows, cols = instance["rows"], instance["cols"]
    rowsum, colsum, hints = instance["rowsum"], instance["colsum"], instance["hints"]
    WATER, SHIP, CIRCLE = instance["WATER"], instance["_SHIP"], instance["CIRCLE"]
    LEFT, RIGHT, TOP, BOTTOM, MIDDLE = (instance[k] for k in ("LEFT", "RIGHT", "TOP", "BOTTOM", "MIDDLE"))
    # One ship per entry of the fleet: fleet_counts lists (length, how many)
    lengths = [size for size, count in instance["fleet_counts"] for _ in range(count)]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Ship k occupies rows r1[k]..r2[k] and columns c1[k]..c2[k]; across[k] = 1 if it lies along a row
    r1, c1, across, r2, c2 = [], [], [], [], []
    for size in lengths:
        a = model.bool()
        r = model.int(0, rows - 1)
        c = model.int(0, cols - 1)
        r1.append(r)
        c1.append(c)
        across.append(a)
        r2.append(r + (size - 1) * (1 - a))
        c2.append(c + (size - 1) * a)
    for k in range(len(lengths)):
        # Every ship lies within the grid
        model.constraint(r2[k] <= rows - 1)
        model.constraint(c2[k] <= cols - 1)
        # A submarine has no orientation; fix it so one placement is one assignment
        if lengths[k] == 1:
            model.constraint(across[k] == 0)
    # No two ships occupy adjacent squares, not even diagonally: their boxes are a square apart
    for k in range(len(lengths)):
        for m in range(k + 1, len(lengths)):
            model.constraint(model.or_(c2[k] + 1 < c1[m], c2[m] + 1 < c1[k], r2[k] + 1 < r1[m], r2[m] + 1 < r1[k]))

    def part(k, i, j):
        """The code ship k puts on square (i, j), or 0 if it does not cover it."""
        on = model.and_(r1[k] <= i, i <= r2[k], c1[k] <= j, j <= c2[k])
        if lengths[k] == 1:
            return CIRCLE * on
        along = model.iif(j == c1[k], LEFT, model.iif(j == c2[k], RIGHT, MIDDLE))
        down = model.iif(i == r1[k], TOP, model.iif(i == r2[k], BOTTOM, MIDDLE))
        return on * model.iif(across[k], along, down)

    # Each square shows water or the part of the ship that covers it (ships never overlap)
    grid = [[model.sum(part(k, i, j) for k in range(len(lengths))) for j in range(cols)] for i in range(rows)]
    occupied = [[grid[i][j] != WATER for j in range(cols)] for i in range(rows)]

    # The numbers of occupied squares in each row and column
    for i in range(rows):
        model.constraint(model.sum(occupied[i]) == rowsum[i])
    for j in range(cols):
        model.constraint(model.sum(occupied[i][j] for i in range(rows)) == colsum[j])
    # The shots already taken: water, a submarine, a given ship part, or a ship of unknown part
    for i, j, code in hints:
        model.constraint(occupied[i][j] if code == SHIP else grid[i][j] == code)

    return optimizer, {"grid": grid}
