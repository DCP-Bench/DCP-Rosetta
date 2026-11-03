"""Candies: give each child at least one candy, more than a lower-rated neighbour, with the fewest candies in total.

The children sit in a line and each has a rating. A child with a higher rating than an
immediate neighbour must get more candies than that neighbour.
"""
import hexaly.optimizer as hx


def build(instance):
    # ratings[i]: the rating score of the child in seat i, in order along the line
    ratings = instance["ratings"]
    n = len(ratings)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[i] is the number of candies for child i: at least 1, and never more than n is needed
    # (a rising run of ratings has at most n children, so an optimal solution never needs more than n)
    x = [model.int(1, n) for _ in range(n)]

    # Of two neighbours, the one with the higher rating gets more candies
    # (equal ratings put no constraint between the two children)
    for i in range(n - 1):
        if ratings[i] > ratings[i + 1]:
            model.constraint(x[i] > x[i + 1])
        elif ratings[i] < ratings[i + 1]:
            model.constraint(x[i] < x[i + 1])

    # Minimise the total number of candies given out; z is also the reported total
    z = model.sum(x)
    model.minimize(z)
    return optimizer, {"x": x, "z": z}
