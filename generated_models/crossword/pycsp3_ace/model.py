# crossword: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python crossword.py

from pycsp3 import *


def create_model(instance):
    """Select 8 of the 15 given words so that the crossword puzzle can be completed:
    the grid has 6 rows and 5 columns, its black squares are marked #, and the
    numbered places 1 to 8 start the words. Each place takes one word of its length,
    crossing squares carry the same letter, and no word is used twice."""
    # The 15 given words, longest first and then alphabetically: word k is words[k].
    words = [
        "HOSES", "LASER", "SAILS", "SHEET", "STEER",
        "HEEL", "HIKE", "KEEL", "KNOT", "LINE",
        "AFT", "ALE", "EEL", "LEE", "TIE",
    ]
    n_words = len(words)
    n_slots = 8  # the numbered places 1 to 8 of the grid
    n_letters = 26  # letters coded A = 0 .. Z = 25

    # The rows (word index, letter codes) of the words of the given length, for a Table.
    def fitting(length):
        return [(k, *[ord(ch) - ord("A") for ch in words[k]]) for k in range(n_words) if len(words[k]) == length]

    # chosen[i]: the index of the word that starts at number i + 1. The output is named E in the
    # dict, because E is a reserved identifier in ACE, so the variable is named for what it holds.
    chosen = VarArray(size=n_slots, dom=range(n_words))

    # The letters of each place, in reading order (across: left to right, down: top to bottom).
    across_1 = VarArray(size=5, dom=range(n_letters))  # place 1: row 1, columns 1 to 5
    down_2 = VarArray(size=5, dom=range(n_letters))    # place 2: column 3, rows 1 to 5
    down_3 = VarArray(size=5, dom=range(n_letters))    # place 3: column 5, rows 1 to 5
    across_4 = VarArray(size=4, dom=range(n_letters))  # place 4: row 3, columns 2 to 5
    down_5 = VarArray(size=4, dom=range(n_letters))    # place 5: column 4, rows 3 to 6
    down_6 = VarArray(size=3, dom=range(n_letters))    # place 6: column 1, rows 4 to 6
    across_7 = VarArray(size=3, dom=range(n_letters))  # place 7: row 4, columns 3 to 5
    across_8 = VarArray(size=5, dom=range(n_letters))  # place 8: row 5, columns 1 to 5

    # Each place with the word it takes and its letters, in number order.
    places = [
        (chosen[0], across_1),
        (chosen[1], down_2),
        (chosen[2], down_3),
        (chosen[3], across_4),
        (chosen[4], down_5),
        (chosen[5], down_6),
        (chosen[6], across_7),
        (chosen[7], across_8),
    ]

    satisfy(
        # Each place is filled by a word of its length, spelled by its letters.
        [Table(scope=[word] + list(letters), supports=fitting(len(letters))) for word, letters in places],
        # The chosen words are different words.
        AllDifferent(chosen),
        # Crossing squares carry the same letter.
        across_1[2] == down_2[0],  # row 1, column 3
        across_1[4] == down_3[0],  # row 1, column 5
        across_4[1] == down_2[2],  # row 3, column 3
        across_4[2] == down_5[0],  # row 3, column 4
        across_4[3] == down_3[2],  # row 3, column 5
        across_7[0] == down_2[3],  # row 4, column 3
        across_7[1] == down_5[1],  # row 4, column 4
        across_7[2] == down_3[3],  # row 4, column 5
        across_8[0] == down_6[1],  # row 5, column 1
        across_8[2] == down_2[4],  # row 5, column 3
        across_8[3] == down_5[2],  # row 5, column 4
        across_8[4] == down_3[4],  # row 5, column 5
    )

    return {"E": chosen}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
