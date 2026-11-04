# csplib_033_word_design: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_033_word_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_033_word_design.py csplib_033_word_design.json

from ortools.sat.python import cp_model

A, C, G, T = 1, 2, 3, 4  # the four letters
GC_LETTERS = 4           # the number of letters from {C, G} in each word
MIN_DIFFERENCES = 4      # the number of positions in which two words must differ


def create_model(instance):
    """Find n_words words of length n over the letters A, C, G and T, such that every word has four
    letters from {C, G}, any two different words differ in at least four positions, and the reverse
    of any word differs from the Watson-Crick complement of any word (the two may be the same word)
    in at least four positions."""
    n = instance["n"]                 # the length of each word
    n_words = instance["num_words"]   # the number of words in the set

    model = cp_model.CpModel()

    # words[i][j] is the letter at position j of word i
    words = [[model.new_int_var(A, T, f"words_{i}_{j}") for j in range(n)] for i in range(n_words)]

    # Each word has four letters from {C, G}.
    for i in range(n_words):
        # gc[j] is true when letter j of word i is C or G
        gc = []
        for j in range(n):
            gc_j = model.new_bool_var(f"gc_{i}_{j}")
            model.add_allowed_assignments([words[i][j], gc_j], [(A, 0), (C, 1), (G, 1), (T, 0)])
            gc.append(gc_j)
        model.add(sum(gc) == GC_LETTERS)

    # Any two different words differ in at least four positions.
    for x in range(n_words):
        for y in range(x + 1, n_words):
            # differ[j] is true when letter j of word x and letter j of word y are different
            differ = []
            for j in range(n):
                differ_j = model.new_bool_var(f"differ_{x}_{y}_{j}")
                model.add(words[x][j] != words[y][j]).only_enforce_if(differ_j)
                model.add(words[x][j] == words[y][j]).only_enforce_if(~differ_j)
                differ.append(differ_j)
            model.add(sum(differ) >= MIN_DIFFERENCES)

    # The reverse of word x differs from the complement of word y in at least four positions,
    # for every pair x, y.
    for x in range(n_words):
        for y in range(n_words):
            # differ[j] is true when letter j of the reversed word x and letter j of the complemented
            # word y are different. Complementary letters, A with T and C with G, add up to 5.
            differ = []
            for j in range(n):
                differ_j = model.new_bool_var(f"rc_differ_{x}_{y}_{j}")
                model.add(words[x][n - 1 - j] + words[y][j] != 5).only_enforce_if(differ_j)
                model.add(words[x][n - 1 - j] + words[y][j] == 5).only_enforce_if(~differ_j)
                differ.append(differ_j)
            model.add(sum(differ) >= MIN_DIFFERENCES)

    return model, {"words": words}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
