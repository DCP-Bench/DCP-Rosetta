"""Hardy's 1729 square: four different numbers from 1 to 100 with a^2 + b^2 = c^2 + d^2."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    numbers = [model.int(1, 100) for _ in range(4)]
    a, b, c, d = numbers
    # The four numbers are all different
    for x in range(4):
        for y in range(x + 1, 4):
            model.constraint(numbers[x] != numbers[y])
    # The sum of the squares of the first two equals the sum of the squares of the other two
    model.constraint(a * a + b * b == c * c + d * d)

    return optimizer, {"a": a, "b": b, "c": c, "d": d}
