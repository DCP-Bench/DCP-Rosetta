# calvin_puzzle: a CPMpy model from DCP Rosetta.
# Download the `calvin_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python calvin_puzzle.py calvin_puzzle.json

import cpmpy as cp


def create_model(instance):
    """Fill an n by n grid with the numbers 1 to n^2 in sequence. The next number goes either
    exactly three squares away horizontally or vertically, or exactly two squares away
    diagonally from the previous one."""
    n = instance["n"]  # the grid has n rows and n columns
    cells = n * n

    # x[i, j] is the number written in row i, column j
    x = cp.intvar(1, cells, shape=(n, n), name="x")

    # The allowed moves from a square, as (rows, columns): three squares along a row or
    # column, or two squares along both axes.
    moves = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]
    # The pairs (from square, to square) one allowed move apart, with the squares
    # numbered row by row (row * n + column).
    allowed = [(i * n + j, (i + di) * n + (j + dj))
               for i in range(n) for j in range(n) for di, dj in moves
               if 0 <= i + di < n and 0 <= j + dj < n]

    # Encoding choice: the rule links consecutive numbers, so it is stated on where each
    # number sits. pos[k] is the square holding the number k + 1, and idx[c] is the
    # number minus 1 in square c; they are inverse permutations of each other.
    pos = cp.intvar(0, cells - 1, shape=cells, name="pos")
    idx = cp.intvar(0, cells - 1, shape=cells, name="idx")

    model = cp.Model()
    model.add(cp.Inverse(pos, idx))
    # Every number from 1 to n^2 is used exactly once (implied by the inverse
    # permutation, and stated for clarity).
    model.add(cp.AllDifferent(pos))
    # The number k + 1 sits one allowed move away from the number k.
    for k in range(cells - 1):
        model.add(cp.Table([pos[k], pos[k + 1]], allowed))
    # The grid shows in each square the number found there (numbers start at 1).
    model.add(x == idx.reshape(n, n) + 1)

    return model, {"x": x}


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
