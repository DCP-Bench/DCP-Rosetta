# csplib_012_nonogram: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_012_nonogram.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_012_nonogram.py csplib_012_nonogram.json

from hermax.model import Model


def post_line(m, name, cells, clue):
    """Post the block clue of one row or one column of a nonogram.

    cells: the 0/1 variables of the line, in order (1 = shaded).
    clue: the block lengths of the line, in order; leading zeros are padding and are dropped.

    The blocks appear in the clue order, with at least one unshaded cell between two
    consecutive blocks. A cell is shaded exactly when some block covers it.
    """
    length = len(cells)
    blocks = [b for b in clue if b > 0]

    # start[j] is the first cell of block j; the block must fit inside the line.
    start = [m.int(f"{name}_start_{j}", 0, length - b) for j, b in enumerate(blocks)]

    # Blocks keep their order: block j+1 starts after block j ends, leaving one gap cell.
    for j in range(len(blocks) - 1):
        m &= (start[j] + blocks[j] + 1 <= start[j + 1])

    # Cell c is shaded exactly when some block covers it. Blocks are separated by gaps,
    # so at most one block covers a cell, and the cell's value is the number of covering blocks.
    for c in range(length):
        covers = []
        for j, b in enumerate(blocks):
            # Block j covers cell c exactly when its start lies in [c - b + 1, c].
            lo = max(0, c - b + 1)
            hi = min(c, length - b)
            if lo <= hi:
                covers.append(start[j].in_range(lo, hi))
        m &= (cells[c] == sum(covers))


def create_model(instance):
    """Shade a grid so that every row and every column shows its clue: the consecutive
    blocks of shaded squares, in order, with the given lengths. There is no objective:
    any board that meets all the clues is a solution."""
    rows = instance["rows"]                # number of rows of the grid
    cols = instance["cols"]                # number of columns of the grid
    row_clues = instance["row_rules"]      # row_clues[i]: block lengths of row i, zero-padded
    col_clues = instance["col_rules"]      # col_clues[j]: block lengths of column j, zero-padded
    # row_rule_len and col_rule_len give the width of the padded clue arrays; the zero padding
    # is dropped below, so they are not needed.

    m = Model()

    # board[i][c] is 1 when the square in row i, column c is shaded, 0 when it is not
    board = m.int_matrix("board", rows, cols, 0, 1)

    # Each row shows its clue.
    for i in range(rows):
        post_line(m, f"row{i}", [board[i][c] for c in range(cols)], row_clues[i])

    # Each column shows its clue.
    for j in range(cols):
        post_line(m, f"col{j}", [board[r][j] for r in range(rows)], col_clues[j])

    return m, {"board": board}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
