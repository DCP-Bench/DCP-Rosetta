# csplib_054_n_queens: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_054_n_queens.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_054_n_queens.py csplib_054_n_queens.json

from pycsp3 import *


def create_model(instance):
    """Place n queens on an n x n chessboard so that no two queens are on the same
    row, column or diagonal."""
    n = instance["n"]  # the board is n x n, and n queens are placed on it

    # queens[i] is the column, from 1 to n, of the queen in the i-th row (rows numbered from 0).
    queens = VarArray(size=n, dom=range(1, n + 1))

    satisfy(
        # No two queens are in the same column.
        AllDifferent(queens),
        # No two queens are on the same diagonal going up to the right: queens[i] + i is different for each row i.
        AllDifferent(queens[i] + i for i in range(n)),
        # No two queens are on the same diagonal going down to the right: queens[i] - i is different for each row i.
        AllDifferent(queens[i] - i for i in range(n)),
    )

    return {"queens": queens}


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
