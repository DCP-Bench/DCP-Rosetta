# csplib_054_n_queens: a CPMpy model from DCP Rosetta.
# Download the `csplib_054_n_queens.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_054_n_queens.py csplib_054_n_queens.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Place n queens on an n x n chessboard so that no two queens are on the same
    row, column or diagonal."""
    n = instance["n"]  # the board size and the number of queens

    # queens[i] is the column (1..n) of the queen in row i
    queens = cp.intvar(1, n, shape=n, name="queens")
    rows = np.arange(n)

    model = cp.Model()
    # No two queens share a column.
    model.add(cp.AllDifferent(queens))
    # No two queens share a diagonal going down to the right (column minus row is constant on it).
    model.add(cp.AllDifferent(queens - rows))
    # No two queens share a diagonal going down to the left (column plus row is constant on it).
    model.add(cp.AllDifferent(queens + rows))

    return model, {"queens": queens}


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
