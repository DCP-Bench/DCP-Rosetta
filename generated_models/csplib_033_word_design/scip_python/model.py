# csplib_033_word_design: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_033_word_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_033_word_design.py csplib_033_word_design.json

import numpy as np
from pyscipopt import Model, quicksum

# The letters are numbered 0 = A, 1 = C, 2 = G, 3 = T in the model. The output
# prints them as 1, 2, 3, 4 (A, C, G, T), as the statement asks.
# The Watson-Crick partner of a letter: A <-> T (0 <-> 3) and C <-> G (1 <-> 2).
COMPLEMENT = [3, 2, 1, 0]


def create_model(instance):
    """Find a set S of num_words words of length n over the alphabet A, C, G, T such
    that each word has exactly 4 letters from {C, G}, any two distinct words differ in
    at least 4 positions, and for any two words x and y of S (possibly the same word)
    the reverse of x and the Watson-Crick complement of y differ in at least 4 positions."""
    n = instance["n"]                  # the length of every word
    num_words = instance["num_words"]  # how many words the set S must contain

    model = Model("csplib_033_word_design")

    # x[k, i, l] is 1 when word k has letter l at position i, and 0 when not.
    x = model.addMatrixVar((num_words, n, 4), vtype="B", name="x")

    # Each position of each word holds exactly one letter.
    model.addMatrixCons(x.sum(axis=2) == 1)

    # Each word has exactly 4 letters from {C, G}, the letters with indices 1 and 2.
    # The 4 is fixed by the statement, not by the instance.
    model.addMatrixCons((x[:, :, 1] + x[:, :, 2]).sum(axis=1) == 4)

    # Distinct words differ in at least 4 positions, so at most n - 4 positions agree.
    # shared[i, l] is 1 when both words have letter l at position i. addConsAnd holds in
    # both directions, so shared is exact; it is set one entry at a time because addConsAnd
    # takes one resultant per call. Each position is one letter, so two words agree at
    # position i in at most one letter, and the agreeing positions are the sum of shared.
    # The 4 is fixed by the statement.
    for k in range(num_words):
        for k2 in range(k + 1, num_words):
            shared = model.addMatrixVar((n, 4), vtype="B")
            for i in range(n):
                for l in range(4):
                    model.addConsAnd([x[k, i, l], x[k2, i, l]], shared[i, l])
            model.addCons(shared.sum() <= n - 4)

    # For every ordered pair of words (k, k2), including k == k2: the reverse of word k and
    # the Watson-Crick complement of word k2 differ in at least 4 positions, so at most n - 4
    # positions agree. Position i of the reverse of word k is position n - 1 - i of word k.
    # The complement of word k2 has letter l at position i when word k2 has letter
    # COMPLEMENT[l] there, so shared[i, l] compares x[k, n - 1 - i, l] with x[k2, i, COMPLEMENT[l]].
    for k in range(num_words):
        for k2 in range(num_words):
            shared = model.addMatrixVar((n, 4), vtype="B")
            for i in range(n):
                for l in range(4):
                    model.addConsAnd([x[k, n - 1 - i, l], x[k2, i, COMPLEMENT[l]]], shared[i, l])
            model.addCons(shared.sum() <= n - 4)

    # Output: word k as letter numbers 1..4 at each position (1 = A, 2 = C, 3 = G, 4 = T).
    # Each entry is the one-hot sum of the letter numbers weighted by their binaries.
    words = (x * np.array([1, 2, 3, 4])).sum(axis=2)
    return model, {"words": words}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
