from hermax.model import Model


def _line_constraints(m, tag, cells, rule):
    """Post the block constraints of one row or column.

    cells: list of IntVar 0/1 for the line.
    rule: the clue, leading zeros are padding and are dropped.

    Each block j gets a start variable. Cell c is shaded exactly when some block
    covers it. Consecutive blocks are separated by at least one unshaded cell.
    """
    L = len(cells)
    blocks = [v for v in rule if v > 0]

    if not blocks:
        for c in range(L):
            m &= (cells[c] == 0)
        return

    starts = []
    for j, b in enumerate(blocks):
        s = m.int(f"s_{tag}_{j}", 0, L - b)
        starts.append(s)
        if j > 0:
            prev_b = blocks[j - 1]
            # the block starts after the previous block ends, with one gap cell
            m &= (s >= starts[j - 1] + (prev_b + 1))

    for c in range(L):
        covers = []
        always = False
        for j, b in enumerate(blocks):
            lo = max(0, c - b + 1)
            hi = min(c, L - b)
            if lo > hi:
                continue
            if lo == 0 and hi == L - b:
                always = True
                break
            covers.append(starts[j].in_range(lo, hi))
        if always:
            m &= (cells[c] == 1)
        elif not covers:
            m &= (cells[c] == 0)
        else:
            # cell shaded iff some block covers it
            for cov in covers:
                m &= (~cov) | (cells[c] == 1)
            any_cover = covers[0]
            for cov in covers[1:]:
                any_cover = any_cover | cov
            m &= (cells[c] == 0) | any_cover


def build(instance):
    R = instance["rows"]
    C = instance["cols"]
    row_rules = instance["row_rules"]
    col_rules = instance["col_rules"]

    m = Model()
    # 1 = shaded, 0 = unshaded
    board = m.int_matrix("board", R, C, 0, 1)

    # Row clues: each row is a sequence of blocks separated by gaps.
    for i in range(R):
        cells = [board[i][c] for c in range(C)]
        _line_constraints(m, f"r{i}", cells, row_rules[i])

    # Column clues: the same rule applied to each column.
    for j in range(C):
        cells = [board[r][j] for r in range(R)]
        _line_constraints(m, f"c{j}", cells, col_rules[j])

    return m, {"board": board}
