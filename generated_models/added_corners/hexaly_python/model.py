"""Added corners: the digits 1..8 in the circles (corners) and squares (edges) of a 3 x 3 frame, each square the
sum of the two adjoining circles.

    C F C        positions 0 1 2
    F   F                  3   4
    C F C                  5 6 7
"""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # positions[i] is the digit in position i, reading left to right, top to bottom; the digits
    # 1..8 are each used once: a full list decision
    perm = model.list(8)
    model.constraint(model.count(perm) == 8)
    p = [perm[i] + 1 for i in range(8)]

    # Each square equals the sum of the circles next to it
    model.constraint(p[1] == p[0] + p[2])  # top edge: top-left and top-right circles
    model.constraint(p[3] == p[0] + p[5])  # left edge: top-left and bottom-left circles
    model.constraint(p[4] == p[2] + p[7])  # right edge: top-right and bottom-right circles
    model.constraint(p[6] == p[5] + p[7])  # bottom edge: bottom-left and bottom-right circles

    return optimizer, {"positions": p}
