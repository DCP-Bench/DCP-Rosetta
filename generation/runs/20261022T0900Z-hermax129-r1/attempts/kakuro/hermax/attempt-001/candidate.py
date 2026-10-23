from hermax.model import Model


def build(instance):
    n = instance["n"]
    # Non-white cells (black and clue cells), 1-indexed in the data.
    blanks = {(r - 1, c - 1) for r, c in instance["blanks"]}
    entries = instance["problem"]  # each entry: [clue_sum, [r, c], [r, c], ...]

    m = Model()

    # Digit per cell: white cells take 1..9, blank cells are 0.
    x = m.int_matrix("x", n, n, 0, 9)
    for r in range(n):
        for c in range(n):
            if (r, c) in blanks:
                m &= (x[r][c] == 0)
            else:
                m &= (x[r][c] >= 1)

    for clue, *cells in entries:
        cell_vars = [x[r - 1][c - 1] for r, c in cells]

        # Each entry sums to its clue.
        m &= (sum(cell_vars) == clue)

        # No digit is duplicated within an entry.
        for i in range(len(cell_vars)):
            for j in range(i + 1, len(cell_vars)):
                m &= (cell_vars[i] != cell_vars[j])

    return m, {"x": x}
