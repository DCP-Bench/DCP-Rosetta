# knights_tour: a Z3 (Python) model from DCP Rosetta.
# Download the `knights_tour.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python knights_tour.py knights_tour.json

import z3


def create_model(instance):
    """A knight visits every square of an n by n chessboard exactly once, without
    returning to the starting square. The tour numbers the squares by move, from 0."""
    n = instance["n"]  # the board is n by n
    last = n * n - 1   # the last move number
    cells = [(i, j) for i in range(n) for j in range(n)]

    # The knight's moves as (row step, column step).
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

    # The squares a knight can reach from square (i, j) in one move.
    def jumps(i, j):
        return [(i + di, j + dj) for di, dj in knight_moves
                if 0 <= i + di < n and 0 <= j + dj < n]

    # x[i][j] is the move at which the knight visits square (i, j).
    x = [[z3.Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    # visit[k][(i, j)] is true when the knight is on square (i, j) at move k.
    visit = [{p: z3.Bool(f"visit_{k}_{p[0]}_{p[1]}") for p in cells} for k in range(last + 1)]

    # start_odd is true when the starting square has an odd sum of row and column.
    start_odd = z3.Bool("start_odd")

    solver = z3.Solver()

    # Every square has a move number from 0 to n*n-1.
    for i, j in cells:
        solver.add(x[i][j] >= 0, x[i][j] <= last)

    # The move number of each square is the move at which the knight is on it.
    for k in range(last + 1):
        for p in cells:
            solver.add(z3.Implies(visit[k][p], x[p[0]][p[1]] == k))

    # Each square is visited at exactly one move.
    for p in cells:
        solver.add(z3.PbEq([(visit[k][p], 1) for k in range(last + 1)], 1))

    # Each move is made on exactly one square.
    for k in range(last + 1):
        solver.add(z3.PbEq([(visit[k][p], 1) for p in cells], 1))

    # The square after each move is a knight's move away from the square of that move.
    for k in range(last):
        for p in cells:
            solver.add(z3.Implies(visit[k][p], z3.Or([visit[k + 1][q] for q in jumps(*p)])))

    # The square before each move is a knight's move away from the square of that move.
    for k in range(1, last + 1):
        for p in cells:
            solver.add(z3.Implies(visit[k][p], z3.Or([visit[k - 1][q] for q in jumps(*p)])))

    # A knight changes square colour on every move. The square of move k has the colour of
    # the starting square when k is even, and the other colour when k is odd.
    for k in range(last + 1):
        for p in cells:
            needed_odd = start_odd if k % 2 == 0 else z3.Not(start_odd)
            on_odd_square = (p[0] + p[1]) % 2 == 1
            solver.add(z3.Implies(visit[k][p], needed_odd if on_odd_square else z3.Not(needed_odd)))

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
