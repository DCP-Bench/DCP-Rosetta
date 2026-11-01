# crossword: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
# Run it (after `pip install pychoco numpy`) with:
#   python crossword.py

from pychoco.model import Model


def create_model(instance):
    """Complete the crossword grid with 8 words chosen from a list of 15, so that where two words cross they share the same letter."""
    # The 15 words, sorted longest first and then alphabetically: word 0 is HOSES, word 14 is TIE.
    words = [
        "HOSES", "LASER", "SAILS", "SHEET", "STEER",  # five letters
        "HEEL", "HIKE", "KEEL", "KNOT", "LINE",  # four letters
        "AFT", "ALE", "EEL", "LEE", "TIE",  # three letters
    ]
    n_words = len(words)
    # The length of the longest word.
    longest = max(len(word) for word in words)
    # letters[w][p]: letter p of word w as a number (A=1 to Z=26), padded with 0 to the longest length
    letters = [[ord(ch) - ord("A") + 1 for ch in word] + [0] * (longest - len(word)) for word in words]
    # The grid has eight numbered slots, each filled with one word.
    n_slots = 8
    # Each crossing is (slot a, position in a, slot b, position in b): the letter at that position of the word in slot a is the same cell as the letter at that position of the word in slot b.
    crossings = [
        (0, 2, 1, 0), (0, 4, 2, 0), (3, 1, 1, 2), (3, 2, 4, 0), (3, 3, 2, 2), (6, 0, 1, 3),
        (6, 1, 4, 1), (6, 2, 2, 3), (7, 0, 5, 1), (7, 2, 1, 4), (7, 3, 4, 2), (7, 4, 2, 4),
    ]

    model = Model()

    # E[s] is the index of the word placed in slot s.
    E = [model.intvar(0, n_words - 1, name=f"E_{s}") for s in range(n_slots)]
    # Different slots hold different words.
    model.all_different(E).post()

    # Where two slots cross, the two words have the same letter in the shared cell.
    for slot_a, pos_a, slot_b, pos_b in crossings:
        # The letter the word in slot a has at position pos_a, and the same for slot b.
        letter_a = model.intvar(0, 26, name=f"letter_{slot_a}_{pos_a}")
        letter_b = model.intvar(0, 26, name=f"letter_{slot_b}_{pos_b}")
        model.element(letter_a, [word[pos_a] for word in letters], E[slot_a]).post()
        model.element(letter_b, [word[pos_b] for word in letters], E[slot_b]).post()
        model.arithm(letter_a, "=", letter_b).post()

    return model, {"E": E}, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
