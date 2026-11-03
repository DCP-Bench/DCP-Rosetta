# knights_tour: a Python-MIP (Python) model from DCP Rosetta.
# Download the `knights_tour.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python knights_tour.py knights_tour.json

import mip

# the eight moves a knight can make, as (row step, column step)
KNIGHT_MOVES = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]


def create_model(instance):
    """A knight visits every square of an n by n chessboard exactly once, without
    returning to the square it started from. The output gives the number of the move at
    which the knight visits each square, counting from 0."""
    n = instance["n"]  # the board is n by n
    total = n * n      # the number of squares

    model = mip.Model(solver_name="CBC")

    # every square of the board as (row, col)
    squares = [(i, j) for i in range(n) for j in range(n)]

    def neighbours(i, j):
        """The squares on the board that a knight reaches in one move from square (i, j)."""
        # the squares found so far
        result = []
        for di, dj in KNIGHT_MOVES:
            a, b = i + di, j + dj
            if 0 <= a < n and 0 <= b < n:
                result.append((a, b))
        return result

    # move[(s, q)] is 1 when the knight goes directly from square s to square q, and 0 when not
    move = {}
    for (i, j) in squares:
        for (a, b) in neighbours(i, j):
            move[((i, j), (a, b))] = model.add_var(f"move_{i}_{j}_{a}_{b}", var_type=mip.BINARY)

    # number[(i, j)] is the number of the move at which the knight visits square (i, j)
    number = {(i, j): model.add_var(f"number_{i}_{j}", lb=0, ub=total - 1, var_type=mip.INTEGER)
              for (i, j) in squares}

    # The knight leaves each square at most once and enters each square at most once.
    for (i, j) in squares:
        model.add_constr(mip.xsum(move[((i, j), q)] for q in neighbours(i, j)) <= 1)
        incoming = [move[(s, (i, j))] for s in neighbours(i, j)]
        model.add_constr(mip.xsum(incoming) <= 1)

    # The moves form one path through all the squares, so there are total - 1 moves.
    model.add_constr(mip.xsum(move.values()) == total - 1)

    # Along each move the move number goes up by one, so the moves cannot close a loop.
    # A move that is not made is released by span, the largest move number minus the
    # smallest, plus one.
    span = total
    for (s, q), var in move.items():
        model.add_constr(number[q] >= number[s] + 1 - span * (1 - var))

    # x is the board: the move number of each square, row by row of the board.
    x = [[number[(i, j)] for j in range(n)] for i in range(n)]

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
