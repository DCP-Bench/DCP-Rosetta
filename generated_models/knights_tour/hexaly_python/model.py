"""Knight's tour: a knight visits every square of an n x n board once (an open tour)."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]
    cells = n * n
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # tour[t] is the square (r * n + c) visited at move t: every square once
    tour = model.list(cells)
    model.constraint(model.count(tour) == cells)

    # Each move is a knight's move: one row and two columns apart, or two rows and one column
    for t in range(cells - 1):
        dr = model.abs(tour[t] // n - tour[t + 1] // n)
        dc = model.abs(tour[t] % n - tour[t + 1] % n)
        model.constraint(dr * dc == 2)

    # The move number (0..n*n-1) at which each square is visited
    x = [[model.index(tour, r * n + c) for c in range(n)] for r in range(n)]
    return optimizer, {"x": x}
