# crossword: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
# Run it (after `pip install exact numpy`) with:
#   python crossword.py

from exact import Exact


def create_model(instance):
    """Complete the crossword grid with 8 different words from a list of 15, so that the
    two words at each crossing show the same letter. Choose the word for each of the
    8 slots."""
    # The 15 words, numbered from 0 longest first, then alphabetically.
    words = [
        "HOSES", "LASER", "SAILS", "SHEET", "STEER",
        "HEEL", "HIKE", "KEEL", "KNOT", "LINE",
        "AFT", "ALE", "EEL", "LEE", "TIE",
    ]
    n_words = len(words)
    longest = max(len(word) for word in words)  # the most letters in any word
    # letters[w][p] is letter p of word w as a number (A=1 to Z=26), 0 past the end of a
    # shorter word.
    letters = [[ord(ch) - ord("A") + 1 for ch in word] + [0] * (longest - len(word))
               for word in words]
    n_slots = 8  # the numbered slots of the grid

    # The cells where two slots cross. Letter pos_a of slot a is the same cell as
    # letter pos_b of slot b.
    crossings = [
        [0, 2, 1, 0], [0, 4, 2, 0], [3, 1, 1, 2], [3, 2, 4, 0], [3, 3, 2, 2], [6, 0, 1, 3],
        [6, 1, 4, 1], [6, 2, 2, 3], [7, 0, 5, 1], [7, 2, 1, 4], [7, 3, 4, 2], [7, 4, 2, 4],
    ]

    solver = Exact()

    # Exact identifies its variables by name.
    # uses[s][w] is 1 when slot s holds word w, and 0 when not.
    uses = [[f"uses_{s}_{w}" for w in range(n_words)] for s in range(n_slots)]
    # E[s] is the number of the word placed in slot s.
    E = [f"E_{s}" for s in range(n_slots)]
    for s in range(n_slots):
        solver.addVariable(E[s], 0, n_words - 1)
        for name in uses[s]:
            solver.addVariable(name, 0, 1)

        # Each slot holds exactly one word.
        solver.addConstraint([(1, name) for name in uses[s]], True, 1, True, 1)
        # The number of the word used in slot s is E[s].
        solver.addConstraint([(w, uses[s][w]) for w in range(1, n_words)] + [(-1, E[s])],
                             True, 0, True, 0)

    # Each word is used in at most one slot.
    for w in range(n_words):
        solver.addConstraint([(1, uses[s][w]) for s in range(n_slots)], False, 0, True, 1)

    # Where two slots cross, their words show the same letter in that cell. A pair of
    # words that differ there cannot both be placed.
    for slot_a, pos_a, slot_b, pos_b in crossings:
        for word_a in range(n_words):
            for word_b in range(n_words):
                if letters[word_a][pos_a] != letters[word_b][pos_b]:
                    solver.addConstraint([(1, uses[slot_a][word_a]), (1, uses[slot_b][word_b])],
                                         False, 0, True, 1)

    return solver, {"E": E}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
