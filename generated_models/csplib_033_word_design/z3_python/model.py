# csplib_033_word_design: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_033_word_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_033_word_design.py csplib_033_word_design.json

import z3

A, C, G, T = 1, 2, 3, 4  # the four letters
GC_LETTERS = 4           # the number of letters from {C, G} in each word
MIN_DIFFERENCES = 4      # the number of positions in which two words must differ


def create_model(instance):
    """Find a set of num_words words of length n over the letters A, C, G and T. Each word has four
    letters from {C, G}, any two different words differ in at least four positions, and the reverse
    of any word differs from the Watson-Crick complement of any word (the two may be the same word)
    in at least four positions."""
    n = instance["n"]                  # the length of each word
    num_words = instance["num_words"]  # the number of words in the set

    # words[i][j] is the letter at position j of word i
    words = [[z3.Int(f"words_{i}_{j}") for j in range(n)] for i in range(num_words)]

    # the rules the set of words must follow
    solver = z3.Solver()

    # Every letter is one of A, C, G and T.
    for word in words:
        for letter in word:
            solver.add(z3.And(letter >= A, letter <= T))

    # Each word has four letters from {C, G}.
    for word in words:
        solver.add(z3.Sum([z3.If(z3.Or(letter == C, letter == G), 1, 0) for letter in word]) == GC_LETTERS)

    # Any two different words differ in at least four positions.
    for i in range(num_words):
        for k in range(i + 1, num_words):
            solver.add(z3.Sum([z3.If(words[i][j] != words[k][j], 1, 0) for j in range(n)]) >= MIN_DIFFERENCES)

    # The Watson-Crick complement swaps A with T and C with G, which maps a letter v to 5 - v. The
    # reverse of any word x differs from the complement of any word y in at least four positions,
    # for every pair x, y, the same word included.
    for x in words:
        for y in words:
            solver.add(z3.Sum([z3.If(x[n - 1 - j] != 5 - y[j], 1, 0) for j in range(n)]) >= MIN_DIFFERENCES)

    return solver, {"words": words}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
