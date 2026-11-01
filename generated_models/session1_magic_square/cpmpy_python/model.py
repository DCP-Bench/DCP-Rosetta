# session1_magic_square: a CPMpy model from DCP Rosetta.
# Download the `session1_magic_square.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python session1_magic_square.py session1_magic_square.json

import cpmpy as cp


def create_model(instance):
    """A magic square is an n x n grid in which each cell holds a different
    integer from 1 to n^2 and every row, column and diagonal has the same sum."""
    n = instance["n"]  # the number of rows and columns of the square

    # The common sum is n * (n^2 + 1) / 2: the numbers 1..n^2 total
    # n^2 * (n^2 + 1) / 2, shared equally between n rows.
    magic_sum = n * (n**2 + 1) // 2

    # square[i, j] is the number in row i, column j
    square = cp.intvar(1, n**2, shape=(n, n), name="square")

    model = cp.Model()

    # All numbers in the square are different.
    model.add(cp.AllDifferent(square))

    # Every row adds up to the magic sum.
    model.add(square.sum(axis=1) == magic_sum)

    # Every column adds up to the magic sum.
    model.add(square.sum(axis=0) == magic_sum)

    # The main diagonal adds up to the magic sum.
    model.add(cp.sum(square.diagonal()) == magic_sum)

    # The other diagonal adds up to the magic sum.
    model.add(cp.sum(square[:, ::-1].diagonal()) == magic_sum)

    return model, {"square": square}


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
