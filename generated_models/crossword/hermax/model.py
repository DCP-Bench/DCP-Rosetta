# crossword: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
# Run it (after `pip install hermax`) with:
#   python crossword.py

from hermax.model import Model

# The puzzle is fixed by the statement (the instance file is empty), so its data is written here.
# WORDS: the 15 words, sorted longest first and then alphabetically. Each length is one contiguous run.
WORDS = [
    "HOSES", "LASER", "SAILS", "SHEET", "STEER",  # five letters: indices 0-4
    "HEEL", "HIKE", "KEEL", "KNOT", "LINE",       # four letters: indices 5-9
    "AFT", "ALE", "EEL", "LEE", "TIE",            # three letters: indices 10-14
]

# SLOT_LENGTH[k]: the number of squares of the grid slot numbered k+1 (1 across, 2 down, ..., 8 across).
SLOT_LENGTH = [5, 5, 5, 4, 4, 3, 3, 5]

# CROSSINGS: each square where two slots cross, as (slot a, letter position in a, slot b, letter position in b).
# Slots are 0-based: slot 0 is number 1, slot 1 is number 2, and so on.
CROSSINGS = [
    (0, 2, 1, 0),  # 1 across, 3rd letter = first letter of 2 down
    (0, 4, 2, 0),  # 1 across, 5th letter = first letter of 3 down
    (3, 1, 1, 2),  # 4 across, 2nd letter = 3rd letter of 2 down
    (3, 2, 4, 0),  # 4 across, 3rd letter = first letter of 5 down
    (3, 3, 2, 2),  # 4 across, 4th letter = 3rd letter of 3 down
    (6, 0, 1, 3),  # 7 across, 1st letter = 4th letter of 2 down
    (6, 1, 4, 1),  # 7 across, 2nd letter = 2nd letter of 5 down
    (6, 2, 2, 3),  # 7 across, 3rd letter = 4th letter of 3 down
    (7, 0, 5, 1),  # 8 across, 1st letter = 2nd letter of 6 down
    (7, 2, 1, 4),  # 8 across, 3rd letter = 5th letter of 2 down
    (7, 3, 4, 2),  # 8 across, 4th letter = 3rd letter of 5 down
    (7, 4, 2, 4),  # 8 across, 5th letter = 5th letter of 3 down
]


def create_model(instance):
    """Crossword: fill the 8 numbered slots of the grid with 8 different words from the list of 15,
    so that each word has the length of its slot and every square where two slots cross holds the
    same letter in both words. E[k] is the index (from 0) of the word chosen for number k+1."""
    m = Model()

    # The words of a given length form a contiguous run of WORDS, so a slot's word is one of
    # the indices in its run: each slot gets its own tight domain.
    runs = []
    for length in SLOT_LENGTH:
        runs.append([i for i, word in enumerate(WORDS) if len(word) == length])

    # E[k] is the word placed in slot k+1, as an index into WORDS
    E = [m.int(f"word_in_slot_{k + 1}", run[0], run[-1]) for k, run in enumerate(runs)]

    # The 8 selected words are different from one another.
    m &= m.vector(E).all_different()

    # Where two slots cross, the letter at the crossing square is the same in both words.
    for a, pos_a, b, pos_b in CROSSINGS:
        allowed = [(i, j) for i in runs[a] for j in runs[b] if WORDS[i][pos_a] == WORDS[j][pos_b]]
        m &= m.table([E[a], E[b]], allowed=allowed)

    return m, {"E": E}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
