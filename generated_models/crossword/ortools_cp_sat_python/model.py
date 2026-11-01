# crossword: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
# Run it (after `pip install ortools`) with:
#   python crossword.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Complete the crossword grid with 8 words chosen from a list, so that where two
    words cross they share the same letter."""
    # The 15 words to fill the slots from.
    words = [
        "HOSES", "LASER", "SAILS", "SHEET", "STEER",  # five letters
        "HEEL", "HIKE", "KEEL", "KNOT", "LINE",  # four letters
        "AFT", "ALE", "EEL", "LEE", "TIE",  # three letters
    ]
    n_words = len(words)
    longest = max(len(word) for word in words)
    # letters[w][p]: letter p of word w, with 0 past the end of a shorter word
    letters = [[ord(ch) - ord("A") + 1 for ch in word] + [0] * (longest - len(word)) for word in words]
    # the number of slots in the grid
    n_slots = 8

    # The cells where two slots cross, with the position of the shared letter in each word.
    crossings = [
        [0, 2, 1, 0], [0, 4, 2, 0], [3, 1, 1, 2], [3, 2, 4, 0], [3, 3, 2, 2], [6, 0, 1, 3],
        [6, 1, 4, 1], [6, 2, 2, 3], [7, 0, 5, 1], [7, 2, 1, 4], [7, 3, 4, 2], [7, 4, 2, 4],
    ]

    model = cp_model.CpModel()

    # E[s] is the index of the word placed in slot s
    E = [model.new_int_var(0, n_words - 1, f"E_{s}") for s in range(n_slots)]
    # Each word is used in at most one slot.
    model.add_all_different(E)

    for slot_a, pos_a, slot_b, pos_b in crossings:
        # letter_a and letter_b: the letter of the shared cell, read from the word in each slot.
        letter_a = model.new_int_var(0, 26, f"letter_{slot_a}_{pos_a}")
        letter_b = model.new_int_var(0, 26, f"letter_{slot_b}_{pos_b}")
        # The word in each slot has that letter at its position.
        model.add_element(E[slot_a], [word[pos_a] for word in letters], letter_a)
        model.add_element(E[slot_b], [word[pos_b] for word in letters], letter_b)
        # The two words agree on the shared cell.
        model.add(letter_a == letter_b)

    return model, {"E": E}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
