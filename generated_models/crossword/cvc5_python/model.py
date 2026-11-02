# crossword: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
# Run it (after `pip install cvc5 numpy`) with:
#   python crossword.py

import cvc5.pythonic as c5


def create_model(instance):
    """Complete the crossword grid with 8 words chosen from a list of 15, so that where
    two words cross they share the same letter."""
    # The 15 words to choose from, longest first, then alphabetically.
    words = [
        "HOSES", "LASER", "SAILS", "SHEET", "STEER",
        "HEEL", "HIKE", "KEEL", "KNOT", "LINE",
        "AFT", "ALE", "EEL", "LEE", "TIE",
    ]
    n_words = len(words)

    # slots[k]: the grid cells (row, column) of the word that starts at number k + 1
    slots = [
        [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],  # 1: across, row 1
        [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2)],  # 2: down, column 3
        [(0, 4), (1, 4), (2, 4), (3, 4), (4, 4)],  # 3: down, column 5
        [(2, 1), (2, 2), (2, 3), (2, 4)],          # 4: across, row 3
        [(2, 3), (3, 3), (4, 3), (5, 3)],          # 5: down, column 4
        [(3, 0), (4, 0), (5, 0)],                  # 6: down, column 1
        [(3, 2), (3, 3), (3, 4)],                  # 7: across, row 4
        [(4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],  # 8: across, row 5
    ]

    # E[k] is the index in the list above of the word placed at number k + 1
    E = [c5.Int(f"E_{k}") for k in range(len(slots))]

    # cells[(row, column)] is the letter in each cell that a word covers
    cells = {}
    for slot in slots:
        for cell in slot:
            if cell not in cells:
                cells[cell] = c5.Int(f"cell_{cell[0]}_{cell[1]}")

    solver = c5.Solver()

    # Each number gets one of the 15 words.
    solver.add([c5.And(0 <= e, e <= n_words - 1) for e in E])

    # The 8 chosen words are all different.
    solver.add(c5.Distinct(E))

    # Each cell holds a letter from A to Z.
    solver.add([c5.And(65 <= v, v <= 90) for v in cells.values()])

    # The word at a number has the length of that number's slot, and at each cell of the
    # slot it has the letter that the cell holds.
    for k, slot in enumerate(slots):
        e = E[k]
        candidates = [w for w in range(n_words) if len(words[w]) == len(slot)]
        solver.add(c5.Or([e == w for w in candidates]))
        for w in candidates:
            for p, cell in enumerate(slot):
                solver.add(c5.Implies(e == w, cells[cell] == ord(words[w][p])))

    return solver, {"E": E}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
