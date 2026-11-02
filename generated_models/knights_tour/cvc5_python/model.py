# knights_tour: a cvc5 (Python) model from DCP Rosetta.
# Download the `knights_tour.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python knights_tour.py knights_tour.json

import cvc5.pythonic as c5


def exactly_one(options):
    """Exactly one of the Boolean options is true."""
    # At least one option is true.
    constraints = [c5.Or(options)] if len(options) >= 2 else [options[0]]
    # No two options are true together.
    for i in range(len(options)):
        for j in range(i + 1, len(options)):
            constraints.append(c5.Or(c5.Not(options[i]), c5.Not(options[j])))
    return constraints


def create_model(instance):
    """A knight visits every square of an n by n chessboard exactly once, without
    returning to the starting square. The tour numbers the squares by move, from 0."""
    n = instance["n"]  # the board is n by n
    squares = n * n    # the number of squares, numbered p = row * n + column

    def square(r, c):
        return r * n + c

    # The knight's moves as (row step, column step).
    knight_moves = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]

    # neighbours[p] is the squares one knight's move away from square p.
    neighbours = {
        square(r, c): [
            square(r + dr, c + dc)
            for dr, dc in knight_moves
            if 0 <= r + dr < n and 0 <= c + dc < n
        ]
        for r in range(n)
        for c in range(n)
    }

    solver = c5.Solver()

    # x[p] is the move at which the knight visits square p.
    x = [c5.Int(f"x_{p}") for p in range(squares)]
    for v in x:
        solver.add(v >= 0, v <= squares - 1)

    # jump[(p, q)] is true when the knight goes from square p to square q in one move.
    jump = {(p, q): c5.Bool(f"j_{p}_{q}") for p in range(squares) for q in neighbours[p]}

    # first[p] is true when the tour starts on square p, and last[p] when it ends there.
    first = [c5.Bool(f"f_{p}") for p in range(squares)]
    last = [c5.Bool(f"l_{p}") for p in range(squares)]

    # A jump takes the knight one move on, so the move number goes up by one.
    for (p, q), j in jump.items():
        solver.add(c5.Implies(j, x[q] == x[p] + 1))

    # Each square is entered once, by a jump, or is the first square.
    for q in range(squares):
        incoming = [jump[(p, q)] for p in range(squares) if (p, q) in jump] + [first[q]]
        solver.add(*exactly_one(incoming))

    # Each square is left once, by a jump, or is the last square.
    for p in range(squares):
        outgoing = [jump[(p, q)] for q in neighbours[p]] + [last[p]]
        solver.add(*exactly_one(outgoing))

    # The tour has one first square and one last square.
    solver.add(*exactly_one(first))
    solver.add(*exactly_one(last))

    # The first square is visited at move 0, and the last square at the final move.
    for p in range(squares):
        solver.add(c5.Implies(first[p], x[p] == 0))
        solver.add(c5.Implies(last[p], x[p] == squares - 1))

    return solver, {"x": [[x[square(r, c)] for c in range(n)] for r in range(n)]}


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
