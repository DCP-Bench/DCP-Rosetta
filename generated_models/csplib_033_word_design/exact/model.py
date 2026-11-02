# csplib_033_word_design: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_033_word_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_033_word_design.py csplib_033_word_design.json

from exact import Exact


def create_model(instance):
    """Find num_words words of length n over the letters A, C, G and T, such that every word has
    four letters from {C, G}, any two different words differ in at least four positions, and the
    reverse of any word differs from the Watson-Crick complement of any word (the two may be the
    same word) in at least four positions."""
    n = instance["n"]                  # the length of each word
    num_words = instance["num_words"]  # the number of words in the set

    # Letters are numbered A=1, C=2, G=3, T=4, so the Watson-Crick complement of letter a is 5 - a.
    letters = (1, 2, 3, 4)
    n_cg_letters = 4       # the number of letters from {C, G} in each word
    min_differences = 4    # the number of positions in which two words must differ

    solver = Exact()

    # Exact identifies its variables by name.
    # words[i][j] is the letter at position j of word i
    words = [[f"words_{i}_{j}" for j in range(n)] for i in range(num_words)]
    # is_letter[i][j][a] is 1 when the letter at position j of word i is a
    is_letter = [[{a: f"words_{i}_{j}_is_{a}" for a in letters} for j in range(n)]
                 for i in range(num_words)]
    for i in range(num_words):
        for j in range(n):
            solver.addVariable(words[i][j], 1, 4)
            for a in letters:
                solver.addVariable(is_letter[i][j][a], 0, 1)
            # each position holds exactly one letter, and its number is that letter
            solver.addConstraint([(1, is_letter[i][j][a]) for a in letters], True, 1, True, 1)
            solver.addConstraint([(a, is_letter[i][j][a]) for a in letters] + [(-1, words[i][j])],
                                 True, 0, True, 0)

    # Each word has exactly four letters from {C, G}.
    for i in range(num_words):
        solver.addConstraint([(1, is_letter[i][j][a]) for j in range(n) for a in (2, 3)],
                             True, n_cg_letters, True, n_cg_letters)

    # Two different words differ in at least four positions. differs[j] can be 1 only where letter j
    # of word x and letter j of word y are different, and at least four of them are 1.
    for x in range(num_words):
        for y in range(x + 1, num_words):
            differs = [f"words_{x}_{y}_differ_at_{j}" for j in range(n)]
            for j in range(n):
                solver.addVariable(differs[j], 0, 1)
                for a in letters:
                    solver.addConstraint([(1, differs[j]), (1, is_letter[x][j][a]), (1, is_letter[y][j][a])],
                                         False, 0, True, 2)
            solver.addConstraint([(1, name) for name in differs], True, min_differences)

    # The reverse of word x differs from the Watson-Crick complement of word y in at least four
    # positions, for every pair x, y, including x = y. Position j of the reverse of x is letter
    # n-1-j of x. differs[j] can be 1 only where that letter is not the complement of letter j of y.
    for x in range(num_words):
        for y in range(num_words):
            differs = [f"reverse_{x}_complement_{y}_differ_at_{j}" for j in range(n)]
            for j in range(n):
                solver.addVariable(differs[j], 0, 1)
                for a in letters:
                    solver.addConstraint([(1, differs[j]), (1, is_letter[x][n - 1 - j][a]),
                                          (1, is_letter[y][j][5 - a])], False, 0, True, 2)
            solver.addConstraint([(1, name) for name in differs], True, min_differences)

    return solver, {"words": words}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
