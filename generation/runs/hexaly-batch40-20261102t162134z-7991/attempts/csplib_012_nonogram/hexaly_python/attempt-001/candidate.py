"""Nonogram: shade grid cells so that every row and column shows its given sequence of shaded blocks."""
import hexaly.optimizer as hx


def build(instance):
    rows, cols = instance["rows"], instance["cols"]
    # Rules are padded with leading zeros to a common length; the non-zero entries are the blocks in order
    row_blocks = [[b for b in rule if b > 0] for rule in instance["row_rules"]]
    col_blocks = [[b for b in rule if b > 0] for rule in instance["col_rules"]]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # board[r][c] = 1 if the cell is shaded
    board = [[model.bool() for _ in range(cols)] for _ in range(rows)]

    def line(cells, blocks):
        """Place the blocks along one row or column and tie its cells to them."""
        size = len(cells)
        # start[i] is the first cell of block i
        start = [model.int(0, size - length) for length in blocks]
        # Blocks keep their order with at least one empty cell between them
        for i in range(len(blocks) - 1):
            model.constraint(start[i] + blocks[i] + 1 <= start[i + 1])
        # A cell is shaded exactly when a block covers it (blocks never overlap)
        for c in range(size):
            covered = [model.and_(start[i] <= c, c < start[i] + blocks[i]) for i in range(len(blocks))]
            model.constraint(cells[c] == model.sum(covered))

    for r in range(rows):
        line(board[r], row_blocks[r])
    for c in range(cols):
        line([board[r][c] for r in range(rows)], col_blocks[c])

    return optimizer, {"board": board}
