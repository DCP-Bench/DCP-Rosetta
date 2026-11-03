"""Four numbers: three integers in 1..10 such that every given number is the sum of a subset of them."""
import hexaly.optimizer as hx


def build(instance):
    numbers = instance["numbers"]  # the given integers (between 1 and 10) that must each be a sum of a subset of the three
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[t] = the t-th of the three integers sought, each between 1 and 10 (the range in the statement)
    x = [model.int(1, 10) for _ in range(3)]
    # List them in non-decreasing order (any order is a solution; this picks one)
    model.constraint(x[0] <= x[1])
    model.constraint(x[1] <= x[2])

    # Every given number is the sum of a subset of the three integers
    for number in numbers:
        # use[t] = 1 if x[t] is in the subset that adds up to this number
        use = [model.bool() for _ in range(3)]
        # The subset is not empty (implied, as every given number is at least 1)
        model.constraint(model.sum(use) >= 1)
        # The integers in the subset add up to the number
        model.constraint(model.sum(u * v for u, v in zip(use, x)) == number)

    return optimizer, {"x": x}
