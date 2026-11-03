"""Dudeney numbers: a perfect cube larger than 1, of at most n digits, whose digits add up to its cube root."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]  # the number has at most n digits
    top = 10 ** n - 1
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    number = model.int(2, top)  # the Dudeney number, a cube above 1
    # The cube root, at most the cube root of the largest n-digit number
    root = model.int(2, round(top ** (1 / 3)) + 1)
    model.constraint(number == root * root * root)

    # The digits of the number (leading zeros allowed) rebuild it and add up to the cube root
    digits = [model.int(0, 9) for _ in range(n)]
    model.constraint(number == model.sum(10 ** k * digits[k] for k in range(n)))
    model.constraint(model.sum(digits) == root)

    return optimizer, {"number": number}
