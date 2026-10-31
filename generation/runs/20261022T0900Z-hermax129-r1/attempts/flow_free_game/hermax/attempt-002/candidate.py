from functools import reduce

from hermax.model import Model


def build(instance):
    board = instance["board"]
    rows, cols = len(board), len(board[0])
    colours = sorted({v for row in board for v in row if v})
    K = max(colours)
    cells = [(r, c) for r in range(rows) for c in range(cols)]

    def neighbours(r, c):
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < rows and 0 <= cc < cols:
                yield (rr, cc)

    m = Model()

    # paint[r][c][k] is true when cell (r, c) carries colour k + 1.
    paint = [[m.bool_vector(f"p_{r}_{c}", K) for c in range(cols)] for r in range(rows)]

    # Every cell carries exactly one colour; the given cells keep theirs.
    for r, c in cells:
        m &= paint[r][c].exactly_one()
        if board[r][c]:
            m &= paint[r][c][board[r][c] - 1]

    # A pipe is a path: each end has one neighbour of its colour, each
    # other cell of a colour has exactly two.
    for r, c in cells:
        for k in range(K):
            same = [paint[nr][nc][k] for nr, nc in neighbours(r, c)]
            if board[r][c]:
                if board[r][c] - 1 == k:
                    m &= (sum(same) == 1)
            else:
                m &= (sum(same) == 2).only_if(paint[r][c][k])

    # No pipe may be a loop detached from its ends: every interior cell needs
    # a same-coloured neighbour with a smaller depth, so each chain leads back
    # to an end.
    depth = [[m.int(f"d_{r}_{c}", 0, rows * cols - 1) for c in range(cols)] for r in range(rows)]
    for r, c in cells:
        if board[r][c]:
            continue
        for k in range(K):
            helpers = []
            for nr, nc in neighbours(r, c):
                q = m.bool()
                m &= (~q | paint[nr][nc][k])
                m &= (depth[nr][nc] < depth[r][c]).only_if(q)
                helpers.append(q)
            clause = reduce(lambda acc, q: acc | q, helpers, ~paint[r][c][k])
            m &= clause

    # The output: the colour of each cell as an integer 1 .. K.
    B = [[m.int(f"b_{r}_{c}", 1, K) for c in range(cols)] for r in range(rows)]
    for r, c in cells:
        m &= (B[r][c] == sum((k + 1) * paint[r][c][k] for k in range(K)))

    return m, {"B": B}
