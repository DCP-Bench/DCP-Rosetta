# calvin_puzzle: a cvc5 (Python) model from DCP Rosetta.
# Download the `calvin_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python calvin_puzzle.py calvin_puzzle.json

import cvc5.pythonic as c5


def create_model(instance):
    """Fill an n by n grid with the numbers 1 to n^2 in sequence. The next number goes either
    exactly three squares away horizontally or vertically, or exactly two squares away
    diagonally from the previous one."""
    n = instance["n"]  # the grid has n rows and n columns
    cells = n * n      # the number of squares, which is also the largest number

    # The squares of the grid, as (row, column) pairs.
    squares = [(i, j) for i in range(n) for j in range(n)]

    # The steps from one square to the next, as (rows, columns): three squares along a row or
    # column, or two squares along a diagonal.
    steps = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]

    # The squares one allowed step away from square (i, j), inside the grid.
    def next_squares(i, j):
        return [(i + di, j + dj) for di, dj in steps if 0 <= i + di < n and 0 <= j + dj < n]

    # placed[v][i][j] is true when the number v + 1 is written in row i, column j.
    placed = [[[c5.Bool(f"placed_{v}_{i}_{j}") for j in range(n)] for i in range(n)]
              for v in range(cells)]

    solver = c5.Solver()

    # Each number from 1 to n^2 is written in exactly one square.
    for v in range(cells):
        solver.add(c5.Or([placed[v][i][j] for i, j in squares]))
        for s, (i, j) in enumerate(squares):
            for k, l in squares[s + 1:]:
                solver.add(c5.Or(c5.Not(placed[v][i][j]), c5.Not(placed[v][k][l])))

    # Each square holds exactly one number.
    for i, j in squares:
        solver.add(c5.Or([placed[v][i][j] for v in range(cells)]))
        for v in range(cells):
            for w in range(v + 1, cells):
                solver.add(c5.Or(c5.Not(placed[v][i][j]), c5.Not(placed[w][i][j])))

    # The number v + 2 is written one allowed step away from the number v + 1.
    for v in range(cells - 1):
        for i, j in squares:
            ok = [placed[v + 1][k][l] for k, l in next_squares(i, j)]
            if not ok:
                solver.add(c5.Not(placed[v][i][j]))
            elif len(ok) == 1:
                solver.add(c5.Or(c5.Not(placed[v][i][j]), ok[0]))
            else:
                solver.add(c5.Or(c5.Not(placed[v][i][j]), c5.Or(ok)))

    # x[i][j] is the number written in row i, column j.
    x = [[c5.Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    for i, j in squares:
        solver.add(x[i][j] == c5.Sum([c5.If(placed[v][i][j], v + 1, 0) for v in range(cells)]))

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
