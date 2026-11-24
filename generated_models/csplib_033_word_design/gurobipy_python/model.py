# csplib_033_word_design: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_033_word_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_033_word_design.py csplib_033_word_design.json

import gurobipy as gp
from gurobipy import GRB

# The alphabet, numbered as the output requires: 1 is A, 2 is C, 3 is G, 4 is T.
LETTERS = range(1, 5)
# C and G, the two letters that count as strong.
STRONG = (2, 3)
# Watson-Crick complement: A and T swap (1 and 4), C and G swap (2 and 3), so the complement of letter l is 5 - l.
COMPLEMENT = 5
# The number of strong letters each word has, fixed by the statement.
STRONG_PER_WORD = 4
# The least number of positions in which two compared words must differ, fixed by the statement.
MIN_DIFFERENCE = 4


def create_model(instance):
    """Find num_words words of length n over the alphabet A, C, G, T so that every word has
    exactly 4 letters from C and G, every two different words differ in at least 4 positions,
    and for every pair of words x and y (x may equal y) the reverse of x and the Watson-Crick
    complement of y differ in at least 4 positions. There is no objective: any such set is a solution."""
    n = instance["n"]  # the length of each word
    num_words = instance["num_words"]  # how many words the set must hold

    model = gp.Model("word_design")

    WORDS = range(num_words)  # word numbers
    POS = range(n)  # letter positions within a word

    # letter[i, j] is the letter at position j of word i, as its number 1 to 4 (A, C, G, T)
    letter = model.addVars(WORDS, POS, lb=1, ub=4, vtype=GRB.INTEGER, name="letter")

    # pick[i, j, l] is 1 when position j of word i holds letter l, and 0 when not
    pick = model.addVars(WORDS, POS, LETTERS, vtype=GRB.BINARY, name="pick")
    # Each position holds exactly one letter (pick.sum(i, j, "*") adds over the four letters)
    model.addConstrs((pick.sum(i, j, "*") == 1 for i in WORDS for j in POS), name="one_letter")
    # letter[i, j] reads the chosen letter's number
    model.addConstrs((letter[i, j] == gp.quicksum(l * pick[i, j, l] for l in LETTERS)
                      for i in WORDS for j in POS), name="letter_value")

    # Each word has exactly 4 symbols from C and G.
    model.addConstrs((gp.quicksum(pick[i, j, s] for j in POS for s in STRONG) == STRONG_PER_WORD
                      for i in WORDS), name="strong")

    # The comparisons: a pair of different words (a, b) compared position by position, and each
    # ordered pair (x, y), x may equal y, compared as reverse(x) against complement(y) (rc = True).
    comparisons = ([(a, b, False) for a in WORDS for b in WORDS if a < b]
                   + [(x, y, True) for x in WORDS for y in WORDS])
    COMPARE = range(len(comparisons))

    # same[k, j] is 1 when comparison k agrees at position j. It is forced to 1 when the two
    # letters agree, so the count of agreeing positions cannot be understated.
    same = model.addVars(COMPARE, POS, vtype=GRB.BINARY, name="same")
    # Two letters agree at a position when they are the same letter; for the reverse-complement
    # comparison the letter of x is read from the mirrored position, and y's letter is complemented.
    model.addConstrs((same[k, j] >= pick[x, n - 1 - j if rc else j, l]
                      + pick[y, j, COMPLEMENT - l if rc else l] - 1
                      for k, (x, y, rc) in enumerate(comparisons) for j in POS for l in LETTERS),
                     name="same_letter")
    # At most n - 4 positions agree, so at least 4 positions differ.
    model.addConstrs((same.sum(k, "*") <= n - MIN_DIFFERENCE for k in COMPARE), name="four_differ")

    # words[i][j] is the letter at position j of word i, as its number
    words = [[letter[i, j] for j in POS] for i in WORDS]

    # No objective is set, so this is a satisfaction model.
    return model, {"words": words}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
