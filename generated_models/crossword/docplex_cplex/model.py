# crossword: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python crossword.py

from docplex.mp.model import Model


def create_model(instance):
    """Crossword: choose 8 of 15 given words for the 8 numbered slots of a fixed grid so that the
    letters agree wherever two slots cross."""
    # The 15 given words, longest first and then alphabetical: word w is the word numbered w in
    # the statement (hoses is 0, tie is 14).
    words = ["hoses", "laser", "sails", "sheet", "steer", "heel", "hike", "keel", "knot",
             "line", "aft", "ale", "eel", "lee", "tie"]
    word_len = 5  # the letters of the longest word
    # table[w][k] is the k-th letter of word w, coded a = 1 .. z = 26, and 0 pads a word shorter
    # than word_len letters
    letter = {chr(ord("a") + k): k + 1 for k in range(26)}
    table = [[letter[ch] for ch in word] + [0] * (word_len - len(word)) for word in words]

    # The crossings of the grid, [slot1, pos1, slot2, pos2]: letter pos1 of the word in slot1 is
    # the same cell as letter pos2 of the word in slot2. Slot s is the number s + 1 of the
    # puzzle, and positions count from 0.
    overlapping = [
        [0, 2, 1, 0],  # 1 across and 2 down share row 1, column 3
        [0, 4, 2, 0],  # 1 across and 3 down share row 1, column 5
        [3, 1, 1, 2],  # 4 across and 2 down share row 3, column 3
        [3, 2, 4, 0],  # 4 across and 5 down share row 3, column 4
        [3, 3, 2, 2],  # 4 across and 3 down share row 3, column 5
        [6, 0, 1, 3],  # 7 across and 2 down share row 4, column 3
        [6, 1, 4, 1],  # 7 across and 5 down share row 4, column 4
        [6, 2, 2, 3],  # 7 across and 3 down share row 4, column 5
        [7, 0, 5, 1],  # 8 across and 6 down share row 5, column 1
        [7, 2, 1, 4],  # 8 across and 2 down share row 5, column 3
        [7, 3, 4, 2],  # 8 across and 5 down share row 5, column 4
        [7, 4, 2, 4],  # 8 across and 3 down share row 5, column 5
    ]
    # The 8 numbered slots of the grid, and the number of cells of each: 1, 2, 3 and 8 take five
    # letters, 4 and 5 take four, 6 and 7 take three.
    slot_length = [5, 5, 5, 4, 4, 3, 3, 5]
    slots = range(len(slot_length))
    word_ids = range(len(words))

    model = Model("crossword")

    # put[s, w] is 1 when word w is written in slot s, and 0 when not
    put = model.binary_var_matrix(slots, word_ids, name="put")

    # Each slot holds exactly one word.
    model.add_constraints(model.sum(put[s, w] for w in word_ids) == 1 for s in slots)
    # The 8 words are selected from the 15 given: no word is used twice.
    model.add_constraints(model.sum(put[s, w] for s in slots) <= 1 for w in word_ids)
    # A word fits a slot only when it has as many letters as the slot has cells.
    model.add_constraints(put[s, w] == 0 for s in slots for w in word_ids
                          if len(words[w]) != slot_length[s])

    # E[s] is the number of the word that starts at number s + 1
    E = [model.sum(w * put[s, w] for w in word_ids) for s in slots]

    # Where two slots cross, the two words have the same letter in that cell.
    for s1, p1, s2, p2 in overlapping:
        model.add_constraint(
            model.sum(table[w][p1] * put[s1, w] for w in word_ids)
            - model.sum(table[w][p2] * put[s2, w] for w in word_ids) == 0)

    return model, {"E": E}


if __name__ == "__main__":
    model, outputs = create_model({})
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
