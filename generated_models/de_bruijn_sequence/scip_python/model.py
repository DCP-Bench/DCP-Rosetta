# de_bruijn_sequence: a SCIP (Python) model from DCP Rosetta.
# Download the `de_bruijn_sequence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python de_bruijn_sequence.py de_bruijn_sequence.json

import numpy as np
from pyscipopt import Model, quicksum


def create_model(instance):
    """A de Bruijn sequence of order n on an alphabet of base symbols is a cyclic
    sequence of base**n digits in which every string of n digits occurs exactly once,
    reading the sequence cyclically (the digits at its end are followed by its start).
    Find one, and print it as a list of digits."""
    k = instance["base"]  # k: the number of symbols in the alphabet, so the digits are 0..k-1
    n = instance["n"]     # n: the length of the strings that must each occur exactly once
    L = k ** n            # L: the number of strings of n digits, which is also the length of the sequence

    model = Model("de_bruijn_sequence")

    # x[i] is the digit at position i of the sequence. Its bounds 0..k-1 come from the alphabet size k.
    x = [model.addVar(f"x_{i}", vtype="I", lb=0, ub=k - 1) for i in range(L)]

    # codes[i] is the string that starts at position i, read as a number in base k (from 0 to L - 1).
    # Positions wrap around the end of the sequence, so every one of the L cyclic strings is counted.
    codes = np.array(
        [quicksum(k ** (n - 1 - j) * x[(i + j) % L] for j in range(n)) for i in range(L)],
        dtype=object,
    )

    # word[i, c] is 1 when the string starting at position i has code c, and 0 otherwise.
    # SCIP has no all-different constraint, so the distinct strings are stated on this one-hot table:
    # every code is taken by exactly one position. With L positions and L codes, each string occurs once.
    word = model.addMatrixVar((L, L), vtype="B", name="word")

    # Each position has exactly one code.
    model.addMatrixCons(word.sum(axis=1) == 1)
    # Each code belongs to exactly one position, so every string of n digits occurs exactly once.
    model.addMatrixCons(word.sum(axis=0) == 1)
    # The code chosen for a position is the code of the string that starts there.
    model.addMatrixCons(word @ np.arange(L) == codes)

    # Satisfaction problem: any sequence that meets the constraints above is an answer, so there is no objective.
    return model, {"de_bruijn": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
