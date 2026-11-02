# de_bruijn_sequence: a PySAT (Python) model from DCP Rosetta.
# Download the `de_bruijn_sequence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python de_bruijn_sequence.py de_bruijn_sequence.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """A de Bruijn sequence of order n on an alphabet of base symbols is a cyclic
    sequence of length base**n in which every string of n symbols occurs exactly
    once as a substring. Find such a sequence."""
    base = instance["base"]  # the number of symbols in the alphabet
    n = instance["n"]        # the length of the strings that must all occur
    n_strings = base ** n    # the number of strings, which is also the length of the sequence

    pool = IDPool()
    # number[i]: the string that starts at position i, read as a number in the given base
    number = [Integer(f"number_{i}", 0, n_strings - 1, vpool=pool) for i in range(n_strings)]
    # digits[i][j]: the j-th symbol of the string that starts at position i, most significant first
    digits = [[Integer(f"digit_{i}_{j}", 0, base - 1, vpool=pool) for j in range(n)]
              for i in range(n_strings)]
    engine = IntegerEngine(vars=number + [d for row in digits for d in row], vpool=pool)

    # Each of the strings of n symbols occurs once, so the numbers of the strings are all different.
    engine.add_alldifferent(number)

    # The number of each string is the number its symbols spell in the given base.
    for i in range(n_strings):
        engine.add_linear(sum(base ** (n - j - 1) * digits[i][j] for j in range(n)) - number[i] == 0)

    # Consecutive strings overlap: the string at i - 1 without its first symbol is the first
    # n - 1 symbols of the string at i.
    for i in range(1, n_strings):
        for j in range(1, n):
            engine.add_equal(digits[i - 1][j], digits[i][j - 1])
    # The sequence is cyclic, so the last string overlaps the first one in the same way.
    for j in range(1, n):
        engine.add_equal(digits[n_strings - 1][j], digits[0][j - 1])

    # The sequence reads the first symbol of each string.
    de_bruijn = [digits[i][0] for i in range(n_strings)]

    return engine.clausify(), {"de_bruijn": de_bruijn}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
