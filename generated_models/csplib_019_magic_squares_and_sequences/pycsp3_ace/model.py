# csplib_019_magic_squares_and_sequences: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_019_magic_squares_and_sequences.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_019_magic_squares_and_sequences.py csplib_019_magic_squares_and_sequences.json

from pycsp3 import *


def create_model(instance):
    """A magic sequence of length n is a sequence of integers x_0, ..., x_{n-1}
    between 0 and n - 1 such that, for every i from 0 to n - 1, the number i
    occurs exactly x_i times in the sequence."""
    n = instance["n"]  # the length of the sequence

    # x[i] is the entry at position i, between 0 and n - 1 as the statement says
    x = VarArray(size=n, dom=range(n))

    satisfy(
        # The number i occurs exactly x[i] times in the sequence, for every i.
        Count(x, value=i) == x[i] for i in range(n)
    )

    return {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
