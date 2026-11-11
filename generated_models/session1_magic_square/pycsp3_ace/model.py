# session1_magic_square: a PyCSP3 model from DCP Rosetta.
# Download the `session1_magic_square.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python session1_magic_square.py session1_magic_square.json

from pycsp3 import *


def create_model(instance):
    """A magic square is an n x n grid (n != 2) such that each cell contains a different integer from 1 to n^2 and the
    sum of the integers in each row, column and diagonal is equal. Find a magic square for a given size n."""
    n = instance["n"]  # the grid has n rows and n columns

    # The magic sum n(n^2 + 1) / 2 given by the statement; it is an integer.
    magic_sum = n * (n * n + 1) // 2

    # square[r][c] is the integer in row r and column c, one of 1 to n^2.
    square = VarArray(size=[n, n], dom=range(1, n * n + 1))

    satisfy(
        # Each cell contains a different integer.
        AllDifferent(square),
        # The integers in each row add up to the magic sum.
        [Sum(row) == magic_sum for row in square],
        # The integers in each column add up to the magic sum.
        [Sum(column) == magic_sum for column in columns(square)],
        # The integers on the main diagonal add up to the magic sum.
        Sum(square[i][i] for i in range(n)) == magic_sum,
        # The integers on the other diagonal add up to the magic sum.
        Sum(square[i][n - 1 - i] for i in range(n)) == magic_sum,
    )

    return {"square": square}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("square", "=")
        for row in outputs["square"]:
            print(values(row))
    else:
        print("No solution:", status())
