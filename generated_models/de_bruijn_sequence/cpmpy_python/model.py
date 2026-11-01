# de_bruijn_sequence: a CPMpy model from DCP Rosetta.
# Download the `de_bruijn_sequence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python de_bruijn_sequence.py de_bruijn_sequence.json

import numpy as np
import cpmpy as cp


def create_model(instance):
    """A de Bruijn sequence B(base, n) is a cyclic sequence of length base**n over an
    alphabet of `base` symbols in which every string of length n occurs exactly once
    as a substring. Find such a sequence."""
    base = instance["base"]  # the size of the alphabet
    n = instance["n"]        # the length of the substrings
    m = base ** n            # the length of the sequence = the number of distinct strings

    # binary[i] holds the n symbols of the string starting at position i (most significant first)
    binary = cp.intvar(0, base - 1, shape=(m, n), name="binary")
    # x[i] is the number (in 0..m-1) read from the string of n symbols starting at position i
    x = cp.intvar(0, m - 1, shape=m, name="x")

    model = cp.Model()

    # x[i] is the number whose digits, in the given base, are the symbols binary[i].
    place_values = base ** np.arange(n - 1, -1, -1)
    model.add(x == binary @ place_values)

    # Every string of length n occurs exactly once, so all the numbers differ.
    model.add(cp.AllDifferent(x))

    # Consecutive strings overlap: dropping the first symbol of the string at i-1
    # gives the first n-1 symbols of the string at i.
    model.add(binary[:-1, 1:] == binary[1:, :-1])

    # The sequence is cyclic, so the last string also overlaps with the first one.
    model.add(binary[-1, 1:] == binary[0, :-1])

    # The sequence is the first symbol of each string.
    de_bruijn = binary[:, 0]

    return model, {"de_bruijn": de_bruijn}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
