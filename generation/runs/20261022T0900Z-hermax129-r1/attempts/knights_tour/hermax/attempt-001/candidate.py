from hermax.model import Model


def build(instance):
    n = instance["n"]
    cells = n * n
    last = cells - 1

    steps = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]

    def neighbours(r, c):
        for dr, dc in steps:
            rr, cc = r + dr, c + dc
            if 0 <= rr < n and 0 <= cc < n:
                yield rr, cc

    m = Model()

    # x[r][c] is the move number of square (r, c): every square gets a distinct
    # move number from 0 to n*n-1.
    x = m.int_matrix("x", n, n, 0, last)
    m &= x.flatten().all_different()

    # nxt[s][d] says the knight moves from square s to square d on the next move.
    nxt = {}
    for r in range(n):
        for c in range(n):
            for rr, cc in neighbours(r, c):
                nxt[(r, c, rr, cc)] = m.bool(f"nxt_{r}_{c}_{rr}_{cc}")

    for r in range(n):
        for c in range(n):
            out = [nxt[(r, c, rr, cc)] for rr, cc in neighbours(r, c)]
            incoming = [nxt[(rr, cc, r, c)] for rr, cc in neighbours(r, c)]

            # Each square except the last visited one is followed by exactly one
            # move: at least one successor, and at most one.
            m &= ((x[r][c] == last) | _any(out))
            for i in range(len(out)):
                for j in range(i + 1, len(out)):
                    m &= (~out[i] | ~out[j])

            # Each square is entered by at most one move.
            for i in range(len(incoming)):
                for j in range(i + 1, len(incoming)):
                    m &= (~incoming[i] | ~incoming[j])

    # The move numbers follow the chosen moves: the square reached on a move has
    # the next move number.
    for r in range(n):
        for c in range(n):
            for rr, cc in neighbours(r, c):
                m &= (x[rr][cc] == x[r][c] + 1).only_if(nxt[(r, c, rr, cc)])

    return m, {"x": x}


def _any(literals):
    expr = literals[0]
    for lit in literals[1:]:
        expr = expr | lit
    return expr
