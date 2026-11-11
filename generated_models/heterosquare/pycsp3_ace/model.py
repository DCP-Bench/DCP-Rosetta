# heterosquare: a PyCSP3 model from DCP Rosetta.
# Download the `heterosquare.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python heterosquare.py heterosquare.json

from pycsp3 import *


def create_model(instance):
    """A heterosquare of order n is an n by n square whose elements are distinct integers
    from 1 to n^2 such that the sums of the rows, columns and diagonals are all different.
    Find a heterosquare of the given order."""
    # The order of the square, from the instance.
    n = instance["n"]
    # The square holds the integers 1 to n_cells, each once.
    n_cells = n * n

    # square[r][c] is the element in row r and column c of the square.
    square = VarArray(size=[n, n], dom=range(1, n_cells + 1))

    satisfy(
        # The elements of the square are distinct integers from 1 to n_cells.
        AllDifferent(square),
        # The sums of the rows, the columns and the two diagonals are all different.
        AllDifferent(
            [Sum(square[r]) for r in range(n)]
            + [Sum(square[:, c]) for c in range(n)]
            + [Sum(square[i][i] for i in range(n))]
            + [Sum(square[i][n - 1 - i] for i in range(n))]
        ),
    )

    return {"x": square}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("x", "=")
        for row in outputs["x"]:
            print(values(row))
    else:
        print("No solution:", status())
