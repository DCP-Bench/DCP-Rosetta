# csplib_033_word_design: a CPMpy model from DCP Rosetta.
# Download the `csplib_033_word_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_033_word_design.py csplib_033_word_design.json

import cpmpy as cp

A, C, G, T = 1, 2, 3, 4  # the letters as numbers; the Watson-Crick complement of letter v is 5 - v
GC_LETTERS = 4           # every word has this many letters from {C, G} (fixed by the problem)
MIN_DIFFERENCES = 4      # positions in which two words must differ (fixed by the problem)


def create_model(instance):
    """Find a set of num_words words of length n over the letters A, C, G, T such that every word
    has four letters from {C, G}, any two different words differ in at least four positions, and
    the reverse of any word x differs from the Watson-Crick complement of any word y (x and y may
    be the same word) in at least four positions."""
    n = instance["n"]                  # the length of each word
    num_words = instance["num_words"]  # the number of words in the set

    # words[i, j] is the j-th letter of word i (1 = A, 2 = C, 3 = G, 4 = T)
    words = cp.intvar(A, T, shape=(num_words, n), name="words")

    model = cp.Model()

    # Each word has four letters from {C, G}.
    for word in words:
        model.add(cp.sum((word == C) | (word == G)) == GC_LETTERS)

    # Any two different words differ in at least four positions.
    for i in range(num_words):
        for k in range(i + 1, num_words):
            model.add(cp.sum(words[i] != words[k]) >= MIN_DIFFERENCES)

    # The reverse of word x differs from the complement of word y (each letter v replaced by 5 - v)
    # in at least four positions, for every ordered pair of words, including x = y.
    for y in words:
        for x in words:
            model.add(cp.sum(x[::-1] != 5 - y) >= MIN_DIFFERENCES)

    return model, {"words": words}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
