# de_bruijn_sequence: an Exact (Python) model from DCP Rosetta.
# Download the `de_bruijn_sequence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python de_bruijn_sequence.py de_bruijn_sequence.json

from exact import Exact


def create_model(instance):
    """A de Bruijn sequence of order n on an alphabet of base symbols is a cyclic
    sequence of length base**n in which every string of n symbols occurs exactly
    once as a substring. Find such a sequence."""
    n_symbols = instance["base"]  # the number of symbols in the alphabet
    n = instance["n"]             # the length of the strings that must all occur
    n_strings = n_symbols**n      # the number of strings, which is also the length of the sequence

    solver = Exact()

    # Exact identifies its variables by name.
    # symbol[i][j] is the j-th symbol of the string that starts at position i
    symbol = [[f"symbol_{i}_{j}" for j in range(n)] for i in range(n_strings)]
    # number[i] is the string that starts at position i, read as a number in base n_symbols
    number = [f"number_{i}" for i in range(n_strings)]
    # is_[i][v] is 1 when the string that starts at position i is the number v
    is_ = [[f"is_{i}_{v}" for v in range(n_strings)] for i in range(n_strings)]
    for i in range(n_strings):
        solver.addVariable(number[i], 0, n_strings - 1)
        for name in symbol[i]:
            solver.addVariable(name, 0, n_symbols - 1)
        for name in is_[i]:
            solver.addVariable(name, 0, 1)

    # Each string is exactly one number, and number[i] is that number.
    for i in range(n_strings):
        solver.addConstraint([(1, is_[i][v]) for v in range(n_strings)], True, 1, True, 1)
        solver.addConstraint([(v, is_[i][v]) for v in range(1, n_strings)] + [(-1, number[i])], True, 0, True, 0)

    # Every number is the string at exactly one position, so all the strings are different.
    for v in range(n_strings):
        solver.addConstraint([(1, is_[i][v]) for i in range(n_strings)], True, 1, True, 1)

    # The symbols of each string, read in order as digits in base n_symbols, give its number.
    for i in range(n_strings):
        solver.addConstraint([(n_symbols ** (n - j - 1), symbol[i][j]) for j in range(n)] + [(-1, number[i])],
                             True, 0, True, 0)

    # Consecutive strings overlap: the last n-1 symbols of string i-1 are the first n-1 symbols of string i.
    for i in range(1, n_strings):
        for j in range(1, n):
            solver.addConstraint([(1, symbol[i - 1][j]), (-1, symbol[i][j - 1])], True, 0, True, 0)

    # The sequence is cyclic, so the last string overlaps with the first one in the same way.
    for j in range(1, n):
        solver.addConstraint([(1, symbol[n_strings - 1][j]), (-1, symbol[0][j - 1])], True, 0, True, 0)

    # The sequence is the first symbol of each string, in order.
    return solver, {"de_bruijn": [symbol[i][0] for i in range(n_strings)]}


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
