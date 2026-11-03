# knights_tour: an Exact (Python) model from DCP Rosetta.
# Download the `knights_tour.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python knights_tour.py knights_tour.json

from exact import Exact


def create_model(instance):
    """A knight visits every square of an n by n chessboard exactly once, without returning to
    its starting square. The tour numbers the squares by move, from 0."""
    n = instance["n"]  # side of the chessboard
    squares = n * n  # the number of squares, which is also the number of moves
    moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]  # the knight's moves, as (row step, column step)

    solver = Exact()

    # Exact identifies its variables by name.
    # holds[i][j][k] is 1 when the knight is on square (i, j) at move k (counting from 0), and 0 when not
    holds = [[[f"square_{i}_{j}_is_move_{k}" for k in range(squares)] for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            for name in holds[i][j]:
                solver.addVariable(name, 0, 1)
            # each square is visited at exactly one move
            solver.addConstraint([(1, name) for name in holds[i][j]], True, 1, True, 1)
    for k in range(squares):
        # each move is made from exactly one square
        solver.addConstraint([(1, holds[i][j][k]) for i in range(n) for j in range(n)], True, 1, True, 1)

    # x[i][j] is the move at which the knight is on square (i, j)
    x = [[f"x_{i}_{j}" for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(x[i][j], 0, squares - 1)
            # x is the move number of the square
            solver.addConstraint([(k, holds[i][j][k]) for k in range(1, squares)] + [(-1, x[i][j])],
                                 True, 0, True, 0)

    # Each move goes to a square one knight's move away. A square visited at move k is followed
    # by a square one knight's move away at move k+1, and preceded by one at move k-1.
    for i in range(n):
        for j in range(n):
            neighbours = [(i + a, j + b) for a, b in moves if 0 <= i + a < n and 0 <= j + b < n]
            for k in range(squares - 1):
                solver.addConstraint([(1, holds[ni][nj][k + 1]) for ni, nj in neighbours]
                                     + [(-1, holds[i][j][k])], True, 0)
            for k in range(1, squares):
                solver.addConstraint([(1, holds[ni][nj][k - 1]) for ni, nj in neighbours]
                                     + [(-1, holds[i][j][k])], True, 0)

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
