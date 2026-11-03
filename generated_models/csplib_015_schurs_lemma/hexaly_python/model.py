"""Schur's lemma: put balls 1..n into c boxes so that no box holds x, y and z with x + y = z."""
import hexaly.optimizer as hx


def build(instance):
    n, c = instance["n"], instance["c"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # in_box[i][j] = 1 if ball i + 1 is in box j + 1
    in_box = [[model.bool() for _ in range(c)] for _ in range(n)]

    # A ball is in exactly one box
    for i in range(n):
        model.constraint(model.sum(in_box[i]) == 1)
    # For every x + y = z (x = y included) and every box, not all three balls are in it
    for x in range(1, n + 1):
        for y in range(x, n + 1 - x):
            z = x + y
            for j in range(c):
                model.constraint(in_box[x - 1][j] + in_box[y - 1][j] + in_box[z - 1][j] <= 2)

    # The box (1..c) of each ball
    balls = [model.sum((j + 1) * in_box[i][j] for j in range(c)) for i in range(n)]
    return optimizer, {"balls": balls}
