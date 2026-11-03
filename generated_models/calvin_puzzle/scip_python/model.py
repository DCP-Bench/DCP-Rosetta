# calvin_puzzle: a SCIP (Python) model from DCP Rosetta.
# Download the `calvin_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python calvin_puzzle.py calvin_puzzle.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Fill an n by n grid with the numbers 1 to n*n, each square getting one
    number and each number placed once. Each number after the first is placed
    either three squares away horizontally or vertically, or two squares away
    diagonally, from the previous number. Output the completed grid."""
    n = instance["n"]   # the side of the grid, so the grid has n * n squares (from the statement)
    N = n * n           # the numbers placed: 1 to N, one per square (from the statement)

    model = Model("calvin_puzzle")

    # v[r, c, k] is 1 when square (r, c) holds the number k + 1, and 0 when not.
    # Binaries, so the bounds 0 and 1 are the domain; no big-M bounds needed.
    v = model.addMatrixVar((n, n, N), vtype="B", name="v")

    # Each square holds exactly one number.
    model.addMatrixCons(v.sum(axis=2) == 1)

    # Each number is placed on exactly one square.
    model.addMatrixCons(v.sum(axis=(0, 1)) == 1)

    # The moves from one number to the next, as (row, column) steps:
    # three squares horizontally or vertically, or two squares diagonally.
    moves = [(0, 3), (0, -3), (3, 0), (-3, 0), (2, 2), (2, -2), (-2, 2), (-2, -2)]

    # If square (r, c) holds the number k + 1, then the number k + 2 is on a square
    # reachable from (r, c) by one move. Only the squares inside the grid are listed.
    # Number k + 2 is on exactly one square, so this leaves exactly one such move.
    for k in range(N - 1):
        for r in range(n):
            for c in range(n):
                reachable = [v[r + dr, c + dc, k + 1]
                             for dr, dc in moves
                             if 0 <= r + dr < n and 0 <= c + dc < n]
                model.addCons(v[r, c, k] <= quicksum(reachable))

    # The grid: square (r, c) shows the number it holds, each number weighted by its value.
    x = [[quicksum((k + 1) * v[r, c, k] for k in range(N)) for c in range(n)]
         for r in range(n)]

    # There is no objective: any grid that meets the rules is an answer.
    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
