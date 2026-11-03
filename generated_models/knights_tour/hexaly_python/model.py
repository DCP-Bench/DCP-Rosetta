"""Knight's tour: a knight visits every square of an n x n board once (an open tour)."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]  # side of the chessboard: n x n squares
    cells = n * n  # number of squares, and the number of positions in the tour
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # tour[t] = the square visited at move t, numbered r * n + c for row r and column c; a list decision of size cells
    tour = model.list(cells)
    # The knight visits every square exactly once: the list must use all n * n squares
    model.constraint(model.count(tour) == cells)

    # Consecutive squares in the tour are a knight's move apart (the tour is open: the last square need not lead back to the first).
    # A knight moves one row and two columns, or two rows and one column, and only those two row/column
    # distance pairs have product 2, so dr * dc == 2 tests for a knight's move
    for t in range(cells - 1):
        dr = model.abs(tour[t] // n - tour[t + 1] // n)
        dc = model.abs(tour[t] % n - tour[t + 1] % n)
        model.constraint(dr * dc == 2)

    # Output: x[r][c] = the move number (0..n*n-1) at which the knight visits square (r, c),
    # which is the position of that square in the tour
    x =[[model.index(tour, r * n + c) for c in range(n)] for r in range(n)]
    return optimizer, {"x": x}
