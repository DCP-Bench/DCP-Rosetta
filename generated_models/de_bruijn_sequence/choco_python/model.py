# de_bruijn_sequence: a Choco-solver (Python) model from DCP Rosetta.
# Download the `de_bruijn_sequence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python de_bruijn_sequence.py de_bruijn_sequence.json

from pychoco.model import Model


def create_model(instance):
    """A de Bruijn sequence B(base, n) is a cyclic sequence of length base**n over an
    alphabet of base symbols in which every string of length n occurs exactly once
    as a substring. Find such a sequence."""
    base = instance["base"]  # the number of symbols in the alphabet
    n = instance["n"]        # the length of the strings that must all appear
    n_windows = base**n      # the length of the sequence, which is also the number of strings

    model = Model()

    # x[i] is the number, in the given base, spelled by the n symbols starting at position i
    x = [model.intvar(0, n_windows - 1, name=f"x_{i}") for i in range(n_windows)]
    # digits[i][j] is the j-th symbol of the string starting at position i, most significant first
    digits = [
        [model.intvar(0, base - 1, name=f"digit_{i}_{j}") for j in range(n)]
        for i in range(n_windows)
    ]

    # Every string of length n occurs exactly once, so the numbers all differ.
    model.all_different(x).post()

    # place_values[j] is the value of the j-th symbol of a string in the given base.
    place_values = [base ** (n - j - 1) for j in range(n)]
    for i in range(n_windows):
        model.scalar(digits[i], place_values, "=", x[i]).post()

    # Consecutive strings overlap: the last n-1 symbols of a string are the first n-1 symbols of the next one.
    for i in range(1, n_windows):
        for j in range(1, n):
            model.arithm(digits[i - 1][j], "=", digits[i][j - 1]).post()
    # The sequence is cyclic, so the last string overlaps with the first one.
    for j in range(1, n):
        model.arithm(digits[n_windows - 1][j], "=", digits[0][j - 1]).post()

    # The sequence is the first symbol of each string.
    de_bruijn = [digits[i][0] for i in range(n_windows)]

    return model, {"de_bruijn": de_bruijn}, None


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
