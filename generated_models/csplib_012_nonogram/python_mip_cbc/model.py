# csplib_012_nonogram: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_012_nonogram.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_012_nonogram.py csplib_012_nonogram.json

import mip


def line_windows(n, lengths, known):
    """For each block of a line of n squares, the squares where it can begin in some arrangement
    of the line that agrees with the squares already known (1 shaded, 0 empty, None unknown)."""
    k = len(lengths)
    # c0[j] and c1[j] count the empty and the shaded known squares among the first j squares.
    c0 = [0] * (n + 1)
    c1 = [0] * (n + 1)
    for j in range(n):
        c0[j + 1] = c0[j] + (known[j] == 0)
        c1[j + 1] = c1[j] + (known[j] == 1)

    def zeros_ok(a, b):  # the squares a up to b - 1 can all be empty
        return c1[b] - c1[a] == 0

    def ones_ok(a, b):  # the squares a up to b - 1 can all be shaded
        return c0[b] - c0[a] == 0

    # ends[t] is the set of squares just after block t - 1 over the arrangements of the first t blocks.
    ends = [{0}]
    # fwd[t] is the set of squares where block t can begin, counting from the left.
    fwd = []
    for t in range(k):
        length = lengths[t]
        gap = 1 if t > 0 else 0
        starts = set()
        nxt = set()
        for e in ends[t]:
            for s in range(e + gap, n - length + 1):
                if not zeros_ok(e, s):
                    break
                if ones_ok(s, s + length):
                    starts.add(s)
                    nxt.add(s + length)
        fwd.append(starts)
        ends.append(nxt)

    # bwd[t] is the set of squares where block t can begin, counting from the right, with the blocks after it fitting.
    bwd = [set() for _ in range(k)]
    for t in reversed(range(k)):
        length = lengths[t]
        starts = set()
        for s in range(0, n - length + 1):
            if not ones_ok(s, s + length):
                continue
            e = s + length
            if t == k - 1:
                if zeros_ok(e, n):
                    starts.add(s)
            else:
                for b in sorted(bwd[t + 1]):
                    if b < e + 1:
                        continue
                    if not zeros_ok(e, b):
                        break
                    starts.add(s)
                    break
        bwd[t] = starts

    return [sorted(fwd[t] & bwd[t]) for t in range(k)]


def propagate(n, lengths, known):
    """Unknown squares of a line of n squares that the clue forces: returns {index: value}."""
    windows = line_windows(n, lengths, known)
    fixed = {}
    # coverable[j] is True when some block can cover square j.
    coverable = [False] * n
    for t, length in enumerate(lengths):
        starts = windows[t]
        if not starts:
            continue
        # The squares that every placement of block t covers are shaded.
        for j in range(starts[-1], starts[0] + length):
            fixed[j] = 1
        for s in starts:
            for j in range(s, s + length):
                coverable[j] = True
    for j in range(n):
        if not coverable[j]:
            fixed[j] = 0
    return {j: v for j, v in fixed.items() if known[j] is None}


def create_model(instance):
    """Shade squares of a grid so that every row and every column reads as its clue: the blocks
    of consecutive shaded squares, in the order of the clue, with at least one empty square
    between two blocks."""
    n_rows = instance["rows"]          # the number of rows
    n_cols = instance["cols"]          # the number of columns
    row_rules = instance["row_rules"]  # row_rules[i]: the clue of row i, as block lengths in order
    col_rules = instance["col_rules"]  # col_rules[j]: the clue of column j, as block lengths in order

    # row_len[i] and col_len[j] list the blocks of each line. Zeros in a clue are padding.
    row_len = [[v for v in row_rules[i] if v > 0] for i in range(n_rows)]
    col_len = [[v for v in col_rules[j] if v > 0] for j in range(n_cols)]

    # known[i][j] is 1 or 0 when the clues force square (i, j) to be shaded or empty, and None when they do not.
    # Lines are checked again and again until no clue forces a new square.
    known = [[None] * n_cols for _ in range(n_rows)]
    changed = True
    while changed:
        changed = False
        for i in range(n_rows):
            for j, v in propagate(n_cols, row_len[i], known[i]).items():
                known[i][j] = v
                changed = True
        for j in range(n_cols):
            column = [known[i][j] for i in range(n_rows)]
            for i, v in propagate(n_rows, col_len[j], column).items():
                known[i][j] = v
                changed = True

    model = mip.Model(solver_name="CBC")

    # x[i][j] is 1 when square (i, j) is shaded. A square the clues force has the forced value as its only possible value.
    x = []
    for i in range(n_rows):
        row = []
        for j in range(n_cols):
            lb, ub = (0, 1) if known[i][j] is None else (known[i][j], known[i][j])
            row.append(model.add_var(f"x_{i}_{j}", var_type=mip.BINARY, lb=lb, ub=ub))
        x.append(row)

    # The shaded squares of one line, given as the list of its squares, with the block lengths of its clue
    # and the squares where each block can begin.
    def add_line(cells, lengths, windows, tag):
        k = len(lengths)
        # start[t] maps each square where block t can begin to the variable that is 1 when block t begins there.
        start = []
        for t in range(k):
            st = {}  # the variables of block t, by square where it begins
            for s in windows[t]:
                st[s] = model.add_var(f"{tag}_st{t}_{s}", var_type=mip.BINARY)
            model.add_constr(mip.xsum(st.values()) == 1)
            start.append(st)

        # Blocks keep the order of the clue, with at least one empty square between two blocks.
        for t in range(k - 1):
            for s, b in start[t + 1].items():
                prev = mip.xsum(
                    start[t][q] for q in start[t] if q <= s - lengths[t] - 1
                )
                model.add_constr(b <= prev)

        # A square is shaded exactly when a block covers it.
        for j, cell in enumerate(cells):
            terms = []
            for t, length in enumerate(lengths):
                terms.extend(
                    start[t][q] for q in start[t] if j - length + 1 <= q <= j
                )
            model.add_constr(cell == mip.xsum(terms))

        # The shaded squares of the line add up to the total length of its blocks.
        model.add_constr(mip.xsum(cells) == sum(lengths))

    # Each row reads as its clue.
    for i in range(n_rows):
        add_line(x[i], row_len[i], line_windows(n_cols, row_len[i], known[i]), f"r{i}")

    # Each column reads as its clue.
    for j in range(n_cols):
        column = [known[i][j] for i in range(n_rows)]
        add_line(
            [x[i][j] for i in range(n_rows)],
            col_len[j],
            line_windows(n_rows, col_len[j], column),
            f"c{j}",
        )

    # Any board that meets the clues is a solution, so there is no objective.
    return model, {"board": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
