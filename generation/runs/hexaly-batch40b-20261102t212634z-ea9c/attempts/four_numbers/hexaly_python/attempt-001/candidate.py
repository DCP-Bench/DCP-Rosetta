"""Four numbers: three integers in 1..10 such that every given number is the sum of a subset of them."""
import hexaly.optimizer as hx


def build(instance):
    numbers = instance["numbers"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # The three integers, between 1 and 10, listed in non-decreasing order (any order is a
    # solution; this picks one)
    x = [model.int(1, 10) for _ in range(3)]
    model.constraint(x[0] <= x[1])
    model.constraint(x[1] <= x[2])

    # Every given number is the sum of a non-empty subset of them: use[t] picks the subset
    for number in numbers:
        use = [model.bool() for _ in range(3)]
        model.constraint(model.sum(use) >= 1)
        model.constraint(model.sum(u * v for u, v in zip(use, x)) == number)

    return optimizer, {"x": x}
