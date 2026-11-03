# crossword: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
# Run it (after `pip install mip numpy`) with:
#   python crossword.py

import mip


def create_model(instance):
    """Complete the 6 by 5 crossword grid with 8 of the 15 words, so that every across
    and down word fits its cells and crossing words agree on the letter they share."""
    # The grid, row by row: '#' is a black cell and '.' a white cell.
    grid = [
        ".....",
        "##.#.",
        "#....",
        ".#...",
        ".....",
        ".##.#",
    ]
    # The 15 words, longest first and then alphabetically, so word 0 is HOSES.
    words = sorted(
        ["AFT", "ALE", "EEL", "HEEL", "HIKE", "HOSES", "KEEL", "KNOT", "LASER", "LEE",
         "LINE", "SAILS", "SHEET", "STEER", "TIE"],
        key=lambda w: (-len(w), w),
    )
    # The number of rows and columns of the grid.
    rows, cols = len(grid), len(grid[0])

    # Whether cell (r, c) lies on the grid and is white.
    def white(r, c):
        return 0 <= r < rows and 0 <= c < cols and grid[r][c] == "."

    # The across and down words, numbered in reading order of their first cell. Each
    # word is the list of cells it fills, in order.
    slots = []
    for r in range(rows):
        for c in range(cols):
            if not white(r, c):
                continue
            if not white(r, c - 1) and white(r, c + 1):
                cells = []
                k = c
                while white(r, k):
                    cells.append((r, k))
                    k += 1
                slots.append(cells)
            if not white(r - 1, c) and white(r + 1, c):
                cells = []
                k = r
                while white(k, c):
                    cells.append((k, c))
                    k += 1
                slots.append(cells)

    model = mip.Model(solver_name="CBC")

    # x[s][w] is 1 when slot s is filled with word w, and 0 when not. Only words as long
    # as the slot are offered.
    x = []
    for s, cells in enumerate(slots):
        x.append({
            w: model.add_var(f"x_{s}_{w}", var_type=mip.BINARY)
            for w, word in enumerate(words) if len(word) == len(cells)
        })

    # Each slot is filled with exactly one word.
    for s in range(len(slots)):
        model += mip.xsum(x[s].values()) == 1

    # Each word of the list is used in at most one slot.
    for w in range(len(words)):
        # the choices that put word w in a slot
        terms = [x[s][w] for s in range(len(slots)) if w in x[s]]
        if terms:
            model += mip.xsum(terms) <= 1

    # The (slot, position) pairs that cover each cell.
    uses_of = {}
    for s, cells in enumerate(slots):
        for p, cell in enumerate(cells):
            uses_of.setdefault(cell, []).append((s, p))
    # The letters that occur in the words.
    letters = sorted(set("".join(words)))
    # Where two slots cross, the words agree on the letter in the shared cell: for each
    # letter, the first slot takes a word with that letter there exactly when the second
    # slot does.
    for uses in uses_of.values():
        if len(uses) < 2:
            continue
        s1, p1 = uses[0]
        for s2, p2 in uses[1:]:
            for letter in letters:
                # the choices that put this letter in the shared cell, one list per slot
                first = [x[s1][w] for w in x[s1] if words[w][p1] == letter]
                second = [x[s2][w] for w in x[s2] if words[w][p2] == letter]
                if not first and not second:
                    continue
                model += mip.xsum(first) - mip.xsum(second) == 0

    # E[s] is the number of the word chosen for slot s.
    E = []
    for s in range(len(slots)):
        e = model.add_var(f"E_{s}", lb=0, ub=len(words) - 1, var_type=mip.INTEGER)
        model += e == mip.xsum(w * v for w, v in x[s].items())
        E.append(e)

    return model, {"E": E}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
