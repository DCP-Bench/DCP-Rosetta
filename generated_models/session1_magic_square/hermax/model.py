# session1_magic_square: a hermax (Python) model from DCP Rosetta.
# Download the `session1_magic_square.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
# Then run it on the first instance (after `pip install hermax`):
#   python session1_magic_square.py session1_magic_square.json

from hermax.model import Model


def create_model(instance):
    """Fill an n x n grid with the different integers 1..n^2 so that every row, every
    column and both diagonals add up to the same sum, n(n^2+1)/2. A satisfaction problem."""
    n = instance["n"]  # n: the side length of the square
    magic_sum = n * (n * n + 1) // 2  # the sum that every row, column and diagonal must reach

    m = Model()

    # square[i][j] is the number written in row i, column j, with values from 1 to n^2
    square = m.int_matrix("square", n, n, 1, n * n)

    # Each cell contains a different integer.
    m &= m.vector([square[i][j] for i in range(n) for j in range(n)]).all_different()

    # Every row adds up to the magic sum.
    for i in range(n):
        m &= (sum(square[i][j] for j in range(n)) == magic_sum)

    # Every column adds up to the magic sum.
    for j in range(n):
        m &= (sum(square[i][j] for i in range(n)) == magic_sum)

    # The main diagonal adds up to the magic sum.
    m &= (sum(square[i][i] for i in range(n)) == magic_sum)

    # The anti-diagonal adds up to the magic sum.
    m &= (sum(square[i][n - 1 - i] for i in range(n)) == magic_sum)

    # The only output is the square itself; the model has no objective.
    return m, {"square": square}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
