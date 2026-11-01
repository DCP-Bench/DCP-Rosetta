# csplib_076_costas_arrays: a CPMpy model from DCP Rosetta.
# Download the `csplib_076_costas_arrays.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_076_costas_arrays.py csplib_076_costas_arrays.json

import cpmpy as cp


def create_model(instance):
    """Place n marks on an n-by-n grid, one per row and one per column, so that the
    n(n-1)/2 vectors between the marks are all different (a Costas array)."""
    n = instance["n"]  # size of the grid and number of marks

    # costas[i] is the column (1 to n) of the mark in row i
    costas = cp.intvar(1, n, shape=n, name="costas")

    model = cp.Model()

    # One mark per column: the columns form a permutation.
    model.add(cp.AllDifferent(costas))

    # Difference triangle: for each distance d between rows, the differences
    # costas[j] - costas[j - d] over all j are pairwise different, so no two
    # vectors between marks are equal. Distance n-1 has a single difference and
    # needs no constraint.
    for d in range(1, n - 1):
        model.add(cp.AllDifferent(costas[d:] - costas[:n - d]))

    return model, {"costas": costas}


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
