# de_bruijn_sequence: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `de_bruijn_sequence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
# Then run it on the first instance (after `pip install ortools`):
#   python de_bruijn_sequence.py de_bruijn_sequence.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A de Bruijn sequence of order n on an alphabet of base symbols is a cyclic
    sequence of length base**n in which every string of n symbols occurs exactly
    once as a substring. Find such a sequence."""
    n_symbols = instance["base"]  # the number of symbols in the alphabet
    n = instance["n"]             # the length of the strings that must all occur
    n_strings = n_symbols**n      # the number of strings, which is also the length of the sequence

    model = cp_model.CpModel()

    # digits[i][j] is the j-th symbol of the string that starts at position i
    digits = [[model.new_int_var(0, n_symbols - 1, f"digit_{i}_{j}") for j in range(n)] for i in range(n_strings)]
    # number[i] is the string that starts at position i, as a number
    number = [model.new_int_var(0, n_strings - 1, f"number_{i}") for i in range(n_strings)]

    # Every string occurs exactly once, so the numbers of the strings all differ.
    model.add_all_different(number)

    # The number of each string is the number its symbols spell.
    for i in range(n_strings):
        model.add(number[i] == sum(digits[i][j] * n_symbols ** (n - 1 - j) for j in range(n)))

    # Consecutive strings overlap: dropping the first symbol of string i-1 leaves the first n-1 symbols of string i.
    for i in range(1, n_strings):
        for j in range(1, n):
            model.add(digits[i - 1][j] == digits[i][j - 1])
    # The sequence is cyclic, so the last string overlaps with the first one.
    for j in range(1, n):
        model.add(digits[n_strings - 1][j] == digits[0][j - 1])

    # The sequence is the first symbol of each string.
    de_bruijn = [digits[i][0] for i in range(n_strings)]

    return model, {"de_bruijn": de_bruijn}


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
