# knights_tour: a PySAT (Python) model from DCP Rosetta.
# Download the `knights_tour.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python knights_tour.py knights_tour.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

# The eight moves of a knight, as (row step, column step).
KNIGHT_MOVES = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]


def create_model(instance):
    """A knight visits every square of an n by n chessboard exactly once, without
    returning to the starting square. The tour numbers the squares by move, from 0."""
    n = instance["n"]  # the board is n by n
    last = n * n - 1   # the number of the last move; the moves are numbered 0 to last

    pool = IDPool()

    # x[i][j] is the move at which the knight visits square (i, j), from 0 to last
    x = [[Integer(f"x_{i}_{j}", 0, last, vpool=pool) for j in range(n)] for i in range(n)]
    # All squares of the board, row by row.
    squares = [square for row in x for square in row]
    engine = IntegerEngine(vars=squares, vpool=pool)

    # Each square is visited at a different move.
    engine.add_alldifferent(squares)
    formula = engine.clausify()

    for i in range(n):
        for j in range(n):
            # The squares on the board that a knight move away from square (i, j).
            reachable = [(i + di, j + dj) for di, dj in KNIGHT_MOVES
                         if 0 <= i + di < n and 0 <= j + dj < n]
            # After a move from square (i, j), the knight is on one of the reachable squares.
            for k in range(last):
                formula.append([-x[i][j].equals(k)] + [x[a][b].equals(k + 1) for a, b in reachable])
            # Before a move onto square (i, j), the knight was on one of the reachable squares.
            for k in range(1, last + 1):
                formula.append([-x[i][j].equals(k)] + [x[a][b].equals(k - 1) for a, b in reachable])

    return formula, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
