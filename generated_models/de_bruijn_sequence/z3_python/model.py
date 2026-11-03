# de_bruijn_sequence: a Z3 (Python) model from DCP Rosetta.
# Download the `de_bruijn_sequence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python de_bruijn_sequence.py de_bruijn_sequence.json

import itertools

import z3


def create_model(instance):
    """A de Bruijn sequence of order n on an alphabet of base symbols is a cyclic
    sequence of length base**n in which every string of n symbols occurs exactly
    once as a substring. Find such a sequence."""
    base = instance["base"]     # the number of symbols in the alphabet
    n = instance["n"]           # the length of the strings that must all occur
    n_strings = base ** n       # the number of strings, which is also the length of the sequence

    # de_bruijn[i] is the symbol at position i of the sequence
    de_bruijn = [z3.Int(f"de_bruijn_{i}") for i in range(n_strings)]

    solver = z3.Solver()

    # Every position holds one of the symbols 0 to base - 1.
    solver.add([z3.And(s >= 0, s <= base - 1) for s in de_bruijn])

    # is_symbol[i][s] is true when position i holds symbol s
    is_symbol = [[de_bruijn[i] == s for s in range(base)] for i in range(n_strings)]

    # The sequence is cyclic: the string at the end wraps round to the start.
    for string in itertools.product(range(base), repeat=n):
        # starts_here[i] is true when the string of n symbols from position i is this string
        starts_here = [
            z3.And([is_symbol[(i + j) % n_strings][string[j]] for j in range(n)])
            for i in range(n_strings)
        ]
        # Every string occurs at exactly one position.
        solver.add(z3.PbEq([(w, 1) for w in starts_here], 1))

    return solver, {"de_bruijn": de_bruijn}


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
