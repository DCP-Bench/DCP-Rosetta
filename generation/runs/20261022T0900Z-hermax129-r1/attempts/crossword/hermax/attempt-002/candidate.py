from hermax.model import Model

# Fixed constants of the problem (the puzzle grid and the word list come from the
# description, not from the instance file, which is empty).
# '.' is an open cell, '#' a black cell. Rows 0..5 top to bottom, columns 0..4.
GRID = [
    ".....",
    "##.#.",
    "#....",
    ".#...",
    ".....",
    ".##.#",
]
WORDS = [
    "AFT", "LASER", "ALE", "LEE", "EEL", "LINE", "HEEL", "SAILS", "HIKE", "SHEET",
    "HOSES", "STEER", "KEEL", "TIE", "KNOT",
]


def build(instance):
    # Word indices follow the description: longest first, then alphabetical.
    words = sorted(WORDS, key=lambda w: (-len(w), w))
    n_words = len(words)
    R, C = len(GRID), len(GRID[0])

    def is_open(r, c):
        return 0 <= r < R and 0 <= c < C and GRID[r][c] == "."

    # Find the slots (runs of length >= 2) and number them in reading order.
    slots = []  # (start_cell, direction, cells)
    for r in range(R):
        for c in range(C):
            if not is_open(r, c):
                continue
            if not is_open(r, c - 1) and is_open(r, c + 1):
                cells = []
                k = c
                while is_open(r, k):
                    cells.append((r, k))
                    k += 1
                slots.append(((r, c), "across", cells))
            if not is_open(r - 1, c) and is_open(r + 1, c):
                cells = []
                k = r
                while is_open(k, c):
                    cells.append((k, c))
                    k += 1
                slots.append(((r, c), "down", cells))

    start_order = []
    for r in range(R):
        for c in range(C):
            if (r, c) not in start_order and any(s[0] == (r, c) for s in slots):
                start_order.append((r, c))
    # Output order: slot numbers 1..8, across before down at the same cell.
    slots.sort(key=lambda s: (start_order.index(s[0]), 0 if s[1] == "across" else 1))

    m = Model()
    X = []        # per slot: Boolean vector over the candidate words of its length
    cands = []    # per slot: word indices of the right length
    E = []        # per slot: word index as an integer
    for s, (_, _, cells) in enumerate(slots):
        L = len(cells)
        cand = [w for w in range(n_words) if len(words[w]) == L]
        xs = m.bool_vector(f"x{s}", len(cand))
        m &= xs.exactly_one()                       # exactly one word per slot
        e = m.int(f"e{s}", 0, n_words - 1)
        m &= (e == sum(cand[k] * xs[k] for k in range(len(cand)) if cand[k] != 0))
        X.append(xs)
        cands.append(cand)
        E.append(e)

    # Each word is used at most once.
    for w in range(n_words):
        lits = [X[s][k] for s in range(len(slots)) for k in range(len(cands[s])) if cands[s][k] == w]
        for a in range(len(lits)):
            for b in range(a + 1, len(lits)):
                m &= (~lits[a] | ~lits[b])

    # Crossing cells: the two words must have the same letter there.
    cell_uses = {}
    for s, (_, _, cells) in enumerate(slots):
        for pos, cell in enumerate(cells):
            cell_uses.setdefault(cell, []).append((s, pos))
    for cell, uses in cell_uses.items():
        if len(uses) < 2:
            continue
        for (s, i) in uses:
            for (t, j) in uses:
                if s >= t:
                    continue
                for k in range(len(cands[s])):
                    for l in range(len(cands[t])):
                        if words[cands[s][k]][i] != words[cands[t][l]][j]:
                            m &= (~X[s][k] | ~X[t][l])

    return m, {"E": E}
