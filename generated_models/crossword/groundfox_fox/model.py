# crossword: a FOX model for GroundFOX from DCP Rosetta.
#
# We are to complete the puzzle
#
# ```text 1 2 3 4 5 +---+---+---+---+---+ Given the list of words: 1 | 1 | | 2 | | 3 | AFT
# LASER +---+---+---+---+---+ ALE LEE 2 | # | # | | # | | EEL LINE +---+---+---+---+---+ HEEL
# SAILS 3 | # | 4 | | 5 | | HIKE SHEET +---+---+---+---+---+ HOSES STEER 4 | 6 | # | 7 | | |
# KEEL TIE +---+---+---+---+---+ KNOT 5 | 8 | | | | | +---+---+---+---+---+ 6 | | # | # | | #
# | The numbers 1,2,3,4,5,6,7,8 in the crossword +---+---+---+---+---+ puzzle correspond to
# the words that will start at those locations. ```
#
# We need to select 8 words from the list of 15 words above, such that the above crossword
# puzzle can be completed.
#
# Print the selected words (E) as a list of 8 integers starting from 0, where E[i] is the word
# that starts at number i+1. Assume that the words are first sorted starting from the longest
# word and then alphabetically. So, word 0 corresponds to HOSES, word 1 to LASER, ..., word 14
# to TIE.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py crossword.json --check

# Word list and grid layout are fixed by the puzzle statement, not by the instance.
WORDS = sorted(
    ["AFT", "ALE", "EEL", "HEEL", "HIKE", "HOSES", "KEEL", "KNOT", "LASER", "LEE",
     "LINE", "SAILS", "SHEET", "STEER", "TIE"],
    key=lambda w: (-len(w), w),
)

GRID = [
    ".....",
    "##.#.",
    "#....",
    ".#...",
    ".....",
    ".##.#",
]


def _slots(grid):
    """Runs of open cells of length >= 2, numbered in reading order of their first cell."""
    rows, cols = len(grid), len(grid[0])
    slots = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "#":
                continue
            if (c == 0 or grid[r][c - 1] == "#") and c + 1 < cols and grid[r][c + 1] != "#":
                cells = []
                k = c
                while k < cols and grid[r][k] != "#":
                    cells.append((r, k))
                    k += 1
                slots.append(cells)
            if (r == 0 or grid[r - 1][c] == "#") and r + 1 < rows and grid[r + 1][c] != "#":
                cells = []
                k = r
                while k < rows and grid[k][c] != "#":
                    cells.append((k, c))
                    k += 1
                slots.append(cells)
    return slots


FOX = """
invocabulary { Slot/1 Word/1 Fit/2 Pair/2 Ok/4 }
outvocabulary { E/2 }
theory {
    ! i [Slot(i)] : ? w [Word(w)] : E(i, w).
    ! i [Slot(i)] : ! w [Word(w)] : ! v [Word(v) & ~(w = v)] : ~E(i, w) | ~E(i, v).
    ! i [Slot(i)] : ! w [Word(w) & ~Fit(i, w)] : ~E(i, w).
    ! w [Word(w)] : ! i [Slot(i)] : ! j [Slot(j) & ~(i = j)] : ~E(i, w) | ~E(j, w).
    ! i [Slot(i)] : ! j [Pair(i, j)] : ! a [Word(a)] : ! b [Word(b) & ~Ok(i, j, a, b)] : ~E(i, a) | ~E(j, b).
}
"""


def structure(instance):
    slots = _slots(GRID)
    n = len(WORDS)
    fit = [(i, w) for i in range(len(slots)) for w in range(n) if len(WORDS[w]) == len(slots[i])]
    pair, ok = [], []
    for i in range(len(slots)):
        for j in range(i + 1, len(slots)):
            crossings = [(p, q) for p, a in enumerate(slots[i]) for q, b in enumerate(slots[j]) if a == b]
            if not crossings:
                continue
            pair.append((i, j))
            for a in range(n):
                for b in range(n):
                    if len(WORDS[a]) != len(slots[i]) or len(WORDS[b]) != len(slots[j]):
                        continue
                    if all(WORDS[a][p] == WORDS[b][q] for p, q in crossings):
                        ok.append((i, j, a, b))
    return {
        "Slot": list(range(len(slots))),
        "Word": list(range(n)),
        "Fit": fit,
        "Pair": pair,
        "Ok": ok,
    }
