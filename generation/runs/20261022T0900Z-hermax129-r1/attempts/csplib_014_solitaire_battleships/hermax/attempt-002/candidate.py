from hermax.model import Model

# Cell codes from the problem description (fixed constants of the problem).
WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE = 0, 2, 3, 4, 5, 6, 7


def build(instance):
    R = instance["rows"]
    C = instance["cols"]
    rowsum = instance["rowsum"]
    colsum = instance["colsum"]
    fleet = instance["fleet_counts"]  # [ship length, number of ships] pairs
    hints = instance["hints"]         # [row, col, code], 0-based

    # Every possible placement of every ship length in the fleet.
    # A placement is (length, cells, codes): the cells it covers and the code of each cell.
    placements = []
    for k, _count in fleet:
        if k == 1:
            # a submarine is a single square, horizontal and vertical are the same
            for r in range(R):
                for c in range(C):
                    placements.append((k, [(r, c)], [CIRCLE]))
            continue
        # horizontal ships: left end, middle parts, right end
        for r in range(R):
            for c in range(C - k + 1):
                cells = [(r, c + j) for j in range(k)]
                codes = [LEFT] + [MIDDLE] * (k - 2) + [RIGHT]
                placements.append((k, cells, codes))
        # vertical ships: top end, middle parts, bottom end
        for r in range(R - k + 1):
            for c in range(C):
                cells = [(r + j, c) for j in range(k)]
                codes = [TOP] + [MIDDLE] * (k - 2) + [BOTTOM]
                placements.append((k, cells, codes))

    N = len(placements)
    m = Model()
    # P[i] is true when placement i is one of the ships in the fleet
    P = [m.bool() for _ in range(N)]

    # Fleet: the number of ships of each length is given.
    for k, count in fleet:
        lits = [P[i] for i in range(N) if placements[i][0] == k]
        m &= (sum(lits) == count)

    # Ships cannot occupy adjacent squares, not even diagonally.
    # Two chosen placements that overlap or touch (Chebyshev distance <= 1) are forbidden.
    for i in range(N):
        cells_i = placements[i][1]
        for j in range(i + 1, N):
            cells_j = placements[j][1]
            touch = False
            for (r1, c1) in cells_i:
                for (r2, c2) in cells_j:
                    if max(abs(r1 - r2), abs(c1 - c2)) <= 1:
                        touch = True
                        break
                if touch:
                    break
            if touch:
                m &= (~P[i]) | (~P[j])

    # Occupancy: a square is occupied exactly when a chosen ship covers it.
    occ = {}
    covering = {}
    for i, (_k, cells, _codes) in enumerate(placements):
        for cell in cells:
            covering.setdefault(cell, []).append(i)
    for r in range(R):
        for c in range(C):
            o = m.bool()
            occ[(r, c)] = o
            idxs = covering.get((r, c), [])
            if not idxs:
                m &= (~o)
                continue
            any_cover = P[idxs[0]]
            for i in idxs[1:]:
                any_cover = any_cover | P[i]
            m &= (~o) | any_cover
            for i in idxs:
                m &= (~P[i]) | o

    # Row and column counts of occupied squares.
    for r in range(R):
        m &= (sum(occ[(r, c)] for c in range(C)) == rowsum[r])
    for c in range(C):
        m &= (sum(occ[(r, c)] for r in range(R)) == colsum[c])

    # The grid: the code of each square, taken from the chosen ship part covering it.
    grid = m.int_matrix("grid", R, C, 0, 7)
    for r in range(R):
        for c in range(C):
            # water when unoccupied
            m &= occ[(r, c)] | (grid[r][c] == WATER)
    for i, (_k, cells, codes) in enumerate(placements):
        for (r, c), code in zip(cells, codes):
            m &= (~P[i]) | (grid[r][c] == code)

    # Shots given in the instance fix some squares.
    for r, c, code in hints:
        m &= (grid[r][c] == code)

    return m, {"grid": grid}
