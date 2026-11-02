# crossword: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
# Run it (after `pip install z3-solver numpy`) with:
#   python crossword.py

import z3


def create_model(instance):
    """Complete the crossword grid with 8 words chosen from a list, so that where two
    words cross they share the same letter."""
    # The 15 words, sorted longest first and then alphabetically: word 0 is HOSES and word 14 is TIE.
    words = [
        "HOSES", "LASER", "SAILS", "SHEET", "STEER",  # five letters
        "HEEL", "HIKE", "KEEL", "KNOT", "LINE",  # four letters
        "AFT", "ALE", "EEL", "LEE", "TIE",  # three letters
    ]
    n_words = len(words)
    longest = max(len(word) for word in words)
    # letters[w][p]: letter p of word w as a number (A=1 ... Z=26), 0 past the end of a shorter word
    letters = [[ord(ch) - ord("A") + 1 for ch in word] + [0] * (longest - len(word)) for word in words]

    # The 8 numbered slots of the grid are slots 0 to 7. A crossing is (slot a, letter position
    # in a, slot b, letter position in b): the two letters are the same cell.
    crossings = [
        (0, 2, 1, 0), (0, 4, 2, 0), (3, 1, 1, 2), (3, 2, 4, 0), (3, 3, 2, 2), (6, 0, 1, 3),
        (6, 1, 4, 1), (6, 2, 2, 3), (7, 0, 5, 1), (7, 2, 1, 4), (7, 3, 4, 2), (7, 4, 2, 4),
    ]

    # E[s] is the number of the word placed in slot s.
    E = [z3.Int(f"E_{s}") for s in range(8)]

    def letter_of(word, position):
        """The letter at this position of the word whose number is word."""
        value = letters[n_words - 1][position]
        for k in range(n_words - 2, -1, -1):
            value = z3.If(word == k, letters[k][position], value)
        return value

    solver = z3.Solver()

    # Each slot holds one of the words, so its number is at least 0 and below n_words.
    solver.add([z3.And(word >= 0, word < n_words) for word in E])

    # Each word fills at most one slot.
    solver.add(z3.Distinct(E))

    # Where two slots cross, their words have the same letter in the shared cell.
    solver.add([letter_of(E[a], pos_a) == letter_of(E[b], pos_b) for a, pos_a, b, pos_b in crossings])

    return solver, {"E": E}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
