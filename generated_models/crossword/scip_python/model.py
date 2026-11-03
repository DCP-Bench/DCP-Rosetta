# crossword: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python crossword.py

from pyscipopt import Model, quicksum

# The grid of the statement, with 0-based (row, column) cells. "#" is a black square, "." an open
# cell, and a number an open cell where the statement starts a word:
#
#        0 1 2 3 4
#     0  1 . 2 . 3
#     1  # # . # .
#     2  # 4 . 5 .
#     3  6 # 7 . .
#     4  8 . . . .
#     5  . # # . #
#
# Each word of the puzzle fills one run of two or more open cells across a row or down a column.
# The eight runs are the eight slots below, in the order of the statement's numbering.
SLOTS = [
    [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],  # 1 across
    [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2)],  # 2 down
    [(0, 4), (1, 4), (2, 4), (3, 4), (4, 4)],  # 3 down
    [(2, 1), (2, 2), (2, 3), (2, 4)],          # 4 across
    [(2, 3), (3, 3), (4, 3), (5, 3)],          # 5 down
    [(3, 0), (4, 0), (5, 0)],                  # 6 down
    [(3, 2), (3, 3), (3, 4)],                  # 7 across
    [(4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],  # 8 across
]

# The 15 words of the statement, sorted as the statement sorts them (longest first, then
# alphabetically). A word's index is its position here: word 0 is HOSES, word 14 is TIE.
WORDS = [
    "HOSES", "LASER", "SAILS", "SHEET", "STEER",  # 0-4: five letters
    "HEEL", "HIKE", "KEEL", "KNOT", "LINE",       # 5-9: four letters
    "AFT", "ALE", "EEL", "LEE", "TIE",            # 10-14: three letters
]


def create_model(instance):
    """Complete the crossword of the statement: put eight different words from the list of
    fifteen into the eight slots of the grid, so that the letters where two words cross agree.
    Output E lists the index of the word in each slot, in the slots' order. The instance file is
    empty ([]), so create_model reads no instance field: the grid and the words come from the
    statement."""
    model = Model("crossword")
    n_slots = len(SLOTS)  # one word for each slot
    n_words = len(WORDS)  # the words to choose from

    # x[s, w] is 1 when word w fills slot s. A word can only fill a slot of its own length,
    # so its upper bound is 0 for every other slot.
    x = model.addMatrixVar(
        (n_slots, n_words), vtype="B", name="x",
        ub=[[int(len(WORDS[w]) == len(SLOTS[s])) for w in range(n_words)]
            for s in range(n_slots)],
    )
    # Every slot is filled by exactly one word ...
    model.addMatrixCons(x.sum(axis=1) == 1)
    # ... and no word fills two slots, so the eight words chosen are different.
    model.addMatrixCons(x.sum(axis=0) <= 1)

    # letter[r, c] is the letter in open cell (r, c), as its place in the alphabet (A = 0 to
    # Z = 25), which is where the bounds come from: the words are written in capital letters.
    cells = sorted({cell for slot in SLOTS for cell in slot})
    letter = {(r, c): model.addVar(name=f"letter_{r}_{c}", vtype="I", lb=0, ub=25)
              for r, c in cells}

    # The letter at each position of a slot's word is the letter in the cell at that position.
    # Two slots that cross share a cell, so the words agree where they cross.
    for s, slot in enumerate(SLOTS):
        for i, (r, c) in enumerate(slot):
            model.addCons(
                letter[r, c] == quicksum(
                    (ord(WORDS[w][i]) - ord("A")) * x[s, w]
                    for w in range(n_words) if len(WORDS[w]) == len(slot)
                )
            )

    # E[s] is the index of the word that fills slot s: the one-hot sum is the output itself.
    E = [quicksum(w * x[s, w] for w in range(n_words)) for s in range(n_slots)]

    # The puzzle has no objective: any completed grid is an answer.
    return model, {"E": E}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
