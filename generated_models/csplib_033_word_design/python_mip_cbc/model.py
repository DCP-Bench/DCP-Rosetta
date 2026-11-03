# csplib_033_word_design: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_033_word_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_033_word_design.py csplib_033_word_design.json

import mip

A, C, G, T = 1, 2, 3, 4  # the four letters; the Watson-Crick complement of letter v is 5 - v
GC_LETTERS = 4           # letters from {C, G} in each word
MIN_DIFFERENCES = 4      # positions in which two words must differ


def create_model(instance):
    """Find a set of num_words words of length n over the letters A, C, G and T such that every word
    has four letters from {C, G}, any two different words differ in at least four positions, and the
    reverse of any word x differs from the Watson-Crick complement of any word y (x and y may be the
    same word) in at least four positions."""
    n = instance["n"]                  # the length of each word
    num_words = instance["num_words"]  # the number of words in the set
    letters = [A, C, G, T]             # the alphabet

    model = mip.Model(solver_name="CBC")

    # x[k][i][c - 1] is 1 when position i of word k is the letter c
    x = [
        [[model.add_var(f"x_{k}_{i}_{c}", var_type=mip.BINARY) for c in letters] for i in range(n)]
        for k in range(num_words)
    ]
    # w[k][i] is the letter at position i of word k, as a number
    w = [
        [model.add_var(f"w_{k}_{i}", lb=A, ub=T, var_type=mip.INTEGER) for i in range(n)]
        for k in range(num_words)
    ]

    def X(k, i, c):
        # the variable saying that position i of word k is the letter c
        return x[k][i][c - 1]

    # Each position of each word holds exactly one letter.
    for k in range(num_words):
        for i in range(n):
            model.add_constr(mip.xsum(X(k, i, c) for c in letters) == 1)

    # The number of the letter at each position is the letter chosen there.
    for k in range(num_words):
        for i in range(n):
            model.add_constr(w[k][i] == mip.xsum(c * X(k, i, c) for c in letters))

    # Each word has exactly GC_LETTERS letters from {C, G}.
    for k in range(num_words):
        model.add_constr(mip.xsum(X(k, i, c) for i in range(n) for c in (C, G)) == GC_LETTERS)

    # Two different words differ in at least MIN_DIFFERENCES positions, so they agree in at most
    # n - MIN_DIFFERENCES positions. agree[i][c - 1] is at least 1 when both words have letter c at
    # position i.
    for k in range(num_words):
        for l in range(k + 1, num_words):
            agree = [
                [model.add_var(f"agree_{k}_{l}_{i}_{c}", lb=0, ub=1) for c in letters]
                for i in range(n)
            ]
            for i in range(n):
                for c in letters:
                    model.add_constr(agree[i][c - 1] >= X(k, i, c) + X(l, i, c) - 1)
            model.add_constr(mip.xsum(v for row in agree for v in row) <= n - MIN_DIFFERENCES)

    # For every pair of words k, l (k = l included), the reverse of word k and the complement of
    # word l differ in at least MIN_DIFFERENCES positions. Position i of the reversed word k is
    # letter n - 1 - i of word k. Position i of the complement of word l is 5 - letter i of word l.
    # The two agree at position i with letter c when word l has letter 5 - c there.
    for k in range(num_words):
        for l in range(num_words):
            agree = [
                [model.add_var(f"rc_agree_{k}_{l}_{i}_{c}", lb=0, ub=1) for c in letters]
                for i in range(n)
            ]
            for i in range(n):
                for c in letters:
                    model.add_constr(agree[i][c - 1] >= X(k, n - 1 - i, c) + X(l, i, 5 - c) - 1)
            model.add_constr(mip.xsum(v for row in agree for v in row) <= n - MIN_DIFFERENCES)

    return model, {"words": w}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
