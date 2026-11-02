"""Pythagorean triplet: natural numbers a < b < c with a^2 + b^2 = c^2 and a + b + c = 1000."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    a, b, c = (model.int(1, 1000) for _ in range(3))
    model.constraint(a < b)
    model.constraint(b < c)

    # The sides of a right triangle
    model.constraint(a * a + b * b == c * c)
    # that add up to 1000
    model.constraint(a + b + c == 1000)

    return optimizer, {"a": a, "b": b, "c": c}
