# csplib_033_word_design: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_033_word_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_033_word_design.py csplib_033_word_design.json

from pychoco.model import Model

A, C, G, T = 1, 2, 3, 4  # the four DNA letters
GC_LETTERS = 4           # the number of C or G letters in each word
MIN_DIFFERENCES = 4      # the least number of positions in which two words differ


def create_model(instance):
    """Find a set of num_words DNA words of length n such that every word has four letters from
    {C, G}, any two different words differ in at least four positions, and for any two words x and
    y (the same word allowed) the reverse of x differs from the Watson-Crick complement of y in at
    least four positions."""
    n_letters = instance["n"]        # the length of each word
    n_words = instance["num_words"]  # the number of words in the set

    model = Model()

    # words[i][j] is the letter at position j of word i
    words = [[model.intvar(A, T, name=f"words_{i}_{j}") for j in range(n_letters)]
             for i in range(n_words)]

    # Each word has exactly GC_LETTERS letters that are C or G.
    for word in words:
        model.among(model.intvar(GC_LETTERS, GC_LETTERS), word, [C, G]).post()

    # Two different words differ in at least MIN_DIFFERENCES positions.
    for i in range(n_words):
        for k in range(i + 1, n_words):
            # differs[j] is true when the two words have different letters at position j
            differs = [model.arithm(words[i][j], "!=", words[k][j]).reify() for j in range(n_letters)]
            model.sum(differs, ">=", MIN_DIFFERENCES).post()

    # The reverse of x and the Watson-Crick complement of y differ in at least MIN_DIFFERENCES
    # positions. Position j of the reverse holds x[n - 1 - j], and the complement of y[j] is the
    # letter that pairs with it: A with T and C with G, so the two letters add up to 5.
    for x in words:
        for y in words:
            # differs[j] is true when the reversed letter and the complemented letter at position j differ
            differs = [model.arithm(x[n_letters - 1 - j], "+", y[j], "!=", 5).reify()
                       for j in range(n_letters)]
            model.sum(differs, ">=", MIN_DIFFERENCES).post()

    return model, {"words": words}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
