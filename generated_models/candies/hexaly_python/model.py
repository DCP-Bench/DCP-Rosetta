"""Candies: give each child at least one candy, more than a lower-rated neighbour, with the fewest candies in total."""
import hexaly.optimizer as hx


def build(instance):
    ratings = instance["ratings"]
    n = len(ratings)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[i] is the number of candies for child i: at least 1, and never more than n is needed
    x = [model.int(1, n) for _ in range(n)]

    # Of two neighbours, the one with the higher rating gets more candies
    for i in range(n - 1):
        if ratings[i] > ratings[i + 1]:
            model.constraint(x[i] > x[i + 1])
        elif ratings[i] < ratings[i + 1]:
            model.constraint(x[i] < x[i + 1])

    # Minimise the total number of candies
    z = model.sum(x)
    model.minimize(z)
    return optimizer, {"x": x, "z": z}
