# csplib_033_word_design: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_033_word_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_033_word_design.py csplib_033_word_design.json

import pulp

A, C, G, T = 1, 2, 3, 4  # the letters, as the output numbers them
LETTERS = (A, C, G, T)
GC_LETTERS = 4           # each word has this many letters from {C, G}
MIN_DIFFERENCE = 4       # two words differ in at least this many positions


def create_model(instance):
    """Find num_words words of length n over the letters A, C, G and T such that every word has
    four letters from {C, G}, any two different words differ in at least four positions, and the
    reverse of any word x differs from the Watson-Crick complement of any word y (x and y may be
    the same word) in at least four positions. The complement of a letter is its partner in the
    pairs A-T and C-G, which is 5 minus the letter."""
    n = instance["n"]                  # length of each word
    num_words = instance["num_words"]  # number of words to find

    problem = pulp.LpProblem("word_design", pulp.LpMinimize)

    # has[i][j][l] is 1 when letter j of word i is the letter l
    has = [[{l: pulp.LpVariable(f"has_{i}_{j}_{l}", cat="Binary") for l in LETTERS}
            for j in range(n)] for i in range(num_words)]

    # words[i][j] is the letter at position j of word i
    words = [[pulp.LpVariable(f"words_{i}_{j}", A, T, cat="Integer") for j in range(n)]
             for i in range(num_words)]

    # Each position holds exactly one letter, and words reads that letter.
    for i in range(num_words):
        for j in range(n):
            problem += pulp.lpSum(has[i][j].values()) == 1
            problem += words[i][j] == pulp.lpSum(l * has[i][j][l] for l in LETTERS)

    # Each word has four letters from {C, G}.
    for i in range(num_words):
        problem += pulp.lpSum(has[i][j][C] + has[i][j][G] for j in range(n)) == GC_LETTERS

    # same[j] is 1 when the two words have the same letter at position j. Two different words
    # differ in at least four positions, so they agree in at most n - 4 positions.
    for x in range(num_words):
        for y in range(x + 1, num_words):
            same = [pulp.LpVariable(f"same_{x}_{y}_{j}", 0, 1) for j in range(n)]
            for j in range(n):
                for l in LETTERS:
                    problem += same[j] >= has[x][j][l] + has[y][j][l] - 1
            problem += pulp.lpSum(same) <= n - MIN_DIFFERENCE

    # The reverse of word x and the complement of word y differ in at least four positions, so
    # they agree in at most n - 4 positions. Position j of the reversed x is letter n-1-j of x,
    # and it agrees with position j of the complemented y when letter n-1-j of x is l and letter
    # j of y is 5 - l.
    for x in range(num_words):
        for y in range(num_words):
            agree = [pulp.LpVariable(f"agree_{x}_{y}_{j}", 0, 1) for j in range(n)]
            for j in range(n):
                for l in LETTERS:
                    problem += agree[j] >= has[x][n - 1 - j][l] + has[y][j][5 - l] - 1
            problem += pulp.lpSum(agree) <= n - MIN_DIFFERENCE

    return problem, {"words": words}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
