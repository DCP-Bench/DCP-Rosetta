"""Flow Free: connect each pair of matching colours with a pipe so that the whole board is covered."""
import hexaly.optimizer as hx


def build(instance):
    board = instance["board"]  # non-zero cells are the ends of a colour's pipe, 0 cells are empty
    n = len(board)
    colours = max(max(row) for row in board)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # B[r][c] is the colour of the cell; the ends keep their colour
    B = [[model.int(1, colours) for _ in range(n)] for _ in range(n)]
    ends = {}
    for r in range(n):
        for c in range(n):
            if board[r][c]:
                model.constraint(B[r][c] == board[r][c])
                ends.setdefault(board[r][c], []).append((r, c))
    # The first end of each colour (in reading order) is where its pipe starts
    starts = {cells[0] for cells in ends.values()}

    # pos[r][c] counts the cells along the pipe from its start, which rules out loops of one colour
    pos = [[model.int(0, n * n - 1) for _ in range(n)] for _ in range(n)]

    for r in range(n):
        for c in range(n):
            around = [(a, b) for a, b in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                      if 0 <= a < n and 0 <= b < n]
            same = [B[r][c] == B[a][b] for a, b in around]
            # A pipe end touches one cell of its colour, any other cell is on the pipe between two
            model.constraint(model.sum(same) == (1 if board[r][c] else 2))
            if (r, c) in starts:
                model.constraint(pos[r][c] == 0)
            else:
                # Every other cell follows exactly one neighbour of its colour along the pipe
                follows = [model.and_(s, pos[a][b] + 1 == pos[r][c]) for s, (a, b) in zip(same, around)]
                model.constraint(model.sum(follows) == 1)

    return optimizer, {"B": B}
