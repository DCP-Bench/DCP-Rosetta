# crossword: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
# Run it (after `pip install cpmpy`) with:
#   python crossword.py

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Complete a crossword grid with 8 words chosen from a list of 15 words, so that
    where two words cross they share the same letter."""
    # The statement fixes the grid and the word list, so the instance is empty.
    # Words are numbered longest first, then alphabetically: word 0 is HOSES, word 14 is TIE.
    words = ["HOSES", "LASER", "SAILS", "SHEET", "STEER", "HEEL", "HIKE", "KEEL",
             "KNOT", "LINE", "AFT", "ALE", "EEL", "LEE", "TIE"]
    longest = max(len(word) for word in words)

    # letters[w, p] is letter p of word w as a number (A=1 ... Z=26), 0 where the word is shorter
    letters = cp.cpm_array(np.array(
        [[ord(ch) - ord("A") + 1 for ch in word] + [0] * (longest - len(word)) for word in words]))

    # The 8 numbered slots of the puzzle are slots 0..7. Each crossing is
    # (slot a, position in a, slot b, position in b): that position of the word in slot a
    # is the same cell as that position of the word in slot b.
    crossings = [
        (0, 2, 1, 0),
        (0, 4, 2, 0),
        (3, 1, 1, 2),
        (3, 2, 4, 0),
        (3, 3, 2, 2),
        (6, 0, 1, 3),
        (6, 1, 4, 1),
        (6, 2, 2, 3),
        (7, 0, 5, 1),
        (7, 2, 1, 4),
        (7, 3, 4, 2),
        (7, 4, 2, 4),
    ]

    # E[s] is the number of the word placed in slot s
    E = cp.intvar(0, len(words) - 1, shape=8, name="E")

    model = cp.Model()
    # Each word is used in at most one slot, so the 8 slots hold different words.
    model.add(cp.AllDifferent(E))
    # Where two slots cross, their words have the same letter in the shared cell.
    for a, position_a, b, position_b in crossings:
        model.add(letters[E[a], position_a] == letters[E[b], position_b])

    return model, {"E": E}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
