"""Curious number: another number, up to 10000, that is a square when 1 is added, as is its half plus 1."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # The number is twice its half, so that the half is a whole number
    half = model.int(1, 5000)
    peculiar = 2 * half
    # Adding 1 to the number gives a square, and adding 1 to its half gives a square
    a, b = model.int(1, 101), model.int(1, 71)
    model.constraint(peculiar + 1 == a * a)
    model.constraint(half + 1 == b * b)
    # Another number than 48, the one the statement gives
    model.constraint(peculiar != 48)

    return optimizer, {"peculiar": peculiar}
