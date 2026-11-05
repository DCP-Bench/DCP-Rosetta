"""Eighteen-hole golf: a course of 18 holes of length 3, 4 or 5 with a total length of 72."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Each hole is 3, 4 or 5 long
    holes = [model.int(3, 5) for _ in range(18)]
    # The course is 72 long in total
    model.constraint(model.sum(holes) == 72)

    return optimizer, {"holes": holes}
