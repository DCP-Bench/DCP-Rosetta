# crossword: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python crossword.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Complete the crossword: choose one different word from the list of 15 for each of the 8 numbered entries, so that the letters where entries cross agree."""
    # The 15 words of the statement, longest first and then alphabetically (word 0 is HOSES).
    # Letters are numbered a = 1 to z = 26 and padded with 0 to five letters.
    words = ["hoses", "laser", "sails", "sheet", "steer", "heel", "hike", "keel", "knot",
             "line", "aft", "ale", "eel", "lee", "tie"]
    word_len = 5
    letters = [[ord(ch) - ord("a") + 1 for ch in w] + [0] * (word_len - len(w)) for w in words]
    # The crossings of the grid as (slot, position, slot, position): the letters at the two
    # positions are equal. Slot k is the entry numbered k + 1 in the grid; positions count
    # from 0, the first letter of the entry.
    overlapping = [
        [0, 2, 1, 0], [0, 4, 2, 0],
        [3, 1, 1, 2], [3, 2, 4, 0], [3, 3, 2, 2],
        [6, 0, 1, 3], [6, 1, 4, 1], [6, 2, 2, 3],
        [7, 0, 5, 1], [7, 2, 1, 4], [7, 3, 4, 2], [7, 4, 2, 4],
    ]
    # slot_len[s]: the number of letters of entry s + 1 in the grid.
    slot_len = [5, 5, 5, 4, 4, 3, 3, 5]
    slots = range(len(slot_len))  # the eight numbered entries of the grid
    word_ids = range(len(words))

    model = gp.Model("crossword")

    # uses[s, w] is 1 when slot s holds word w.
    uses = model.addVars(slots, word_ids, vtype=GRB.BINARY, name="uses")
    # Each slot holds exactly one word.
    model.addConstrs((uses.sum(s, "*") == 1 for s in slots), name="one_word")

    # A word fills its slot exactly: it has the slot's length.
    model.addConstrs((uses[s, w] == 0 for s in slots for w in word_ids if len(words[w]) != slot_len[s]),
                     name="length")

    # Each word is used in at most one slot.
    model.addConstrs((uses.sum("*", w) <= 1 for w in word_ids), name="different")

    # letter[s, p] is the number of the letter at position p of the word in slot s.
    letter = {(s, p): gp.quicksum(letters[w][p] * uses[s, w] for w in word_ids)
              for s in slots for p in range(word_len)}

    # At each crossing the two letters are equal.
    model.addConstrs((letter[s1, p1] == letter[s2, p2] for s1, p1, s2, p2 in overlapping), name="cross")

    # No objective: any assignment satisfying the constraints is a solution.

    # E[s] is the index of the word in slot s, counting words from 0 in the list above.
    return model, {"E": [gp.quicksum(w * uses[s, w] for w in word_ids) for s in slots]}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
