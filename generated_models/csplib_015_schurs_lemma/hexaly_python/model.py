"""Schur's lemma: put balls 1..n into c boxes so that no box holds x, y and z with x + y = z."""
import hexaly.optimizer as hx


def build(instance):
    n, c = instance["n"], instance["c"]  # n = number of balls, labelled 1..n; c = number of boxes
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # in_box[i][j] = 1 if ball i + 1 is in box j + 1 (rows are balls, columns are boxes; the problem's M_ij, shifted to 0-based)
    in_box = [[model.bool() for _ in range(c)] for _ in range(n)]

    # A ball must be in exactly one box
    for i in range(n):
        model.constraint(model.sum(in_box[i]) == 1)
    # For any triple of balls (x, y, z) with x + y = z (x = y allowed), not all are in the same box:
    # for each triple and each box j, in_box[x][j] + in_box[y][j] + in_box[z][j] <= 2.
    # y starts at x so each pair is posted once, and y <= n - x keeps z = x + y within 1..n
    for x in range(1, n + 1):
        for y in range(x, n + 1 - x):
            z = x + y
            for j in range(c):
                model.constraint(in_box[x - 1][j] + in_box[y - 1][j] + in_box[z - 1][j] <= 2)

    # Output: balls[i] = the box (1..c) holding ball i + 1, read off the 0-1 variables
    balls = [model.sum((j + 1) * in_box[i][j] for j in range(c)) for i in range(n)]
    return optimizer, {"balls": balls}
