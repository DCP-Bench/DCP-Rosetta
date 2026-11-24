# csplib_076_costas_arrays: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_076_costas_arrays.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_076_costas_arrays.py csplib_076_costas_arrays.json

from pycsp3 import *


def create_model(instance):
    """A Costas array is a pattern of n marks on an n by n grid, one mark per row and one per column,
    in which the n(n-1)/2 vectors between the marks are all different. Find a Costas array of size n,
    given by the column of the mark in each row (1-based)."""
    # The order n of the array: the grid size and the number of marks.
    n = instance["n"]

    # costas[i] is the column of the mark in row i + 1, a value from 1 to n (the statement's X_{i+1}).
    costas = VarArray(size=n, dom=range(1, n + 1))

    satisfy(
        # The marks are in distinct columns, so the values form a permutation.
        AllDifferent(costas),
        # Each line l of the difference triangle, the differences X_i - X_{i+l} for i = 1 .. n - l,
        # has no value twice. The lines are written as expressions, not as extra variables.
        [AllDifferent(costas[i] - costas[i + l] for i in range(n - l)) for l in range(1, n)],
    )

    return {"costas": costas}


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
