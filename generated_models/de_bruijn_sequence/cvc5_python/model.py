# de_bruijn_sequence: a cvc5 (Python) model from DCP Rosetta.
# Download the `de_bruijn_sequence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python de_bruijn_sequence.py de_bruijn_sequence.json

import cvc5.pythonic as c5


def create_model(instance):
    """A de Bruijn sequence of order n on an alphabet of base symbols is a cyclic
    sequence of length base**n in which every string of n symbols occurs exactly
    once as a substring. Find such a sequence."""
    base = instance["base"]  # the number of symbols in the alphabet
    n = instance["n"]        # the length of the strings that must all occur
    length = base**n         # the length of the sequence, which is also the number of strings

    # symbols[i] is the symbol at position i of the sequence
    symbols = [c5.Int(f"symbol_{i}") for i in range(length)]
    # windows[i] is the string of n symbols that starts at position i, read as a number
    windows = [c5.Int(f"window_{i}") for i in range(length)]

    # Every symbol is one of the base symbols, 0 to base - 1.
    alphabet = [c5.And(s >= 0, s <= base - 1) for s in symbols]

    # The string starting at position i is the n symbols from there on, wrapping around
    # the end, read as a number in base `base`.
    spelling = [
        windows[i] == c5.Sum([symbols[(i + j) % length] * base ** (n - 1 - j) for j in range(n)])
        for i in range(length)
    ]

    # Each number lies between 0 and length - 1.
    window_range = [c5.And(w >= 0, w <= length - 1) for w in windows]

    # The strings all differ, so each of the length strings occurs once.
    different = [c5.Distinct(windows)] if length >= 2 else []

    solver = c5.Solver()

    solver.add(alphabet + spelling + window_range + different)
    return solver, {"de_bruijn": symbols}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
