"""Age changing: applying +2, /8, -3 and *7 in some order to my age gives my husband's age, and applying
them in a different order to his age gives mine."""
from fractions import Fraction
from itertools import permutations

import hexaly.optimizer as hx

# The four operations, each as a function of a value: add 2, divide by 8, subtract 3, multiply by 7
OPERATIONS = [lambda v: v + 2, lambda v: v / 8, lambda v: v - 3, lambda v: v * 7]
ORDERS = list(permutations(range(4)))  # the 24 orders in which the four operations can be applied


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Every order of the operations turns an age x into (num * x + add) / den, a straight line in x.
    # Listing the line of each of the 24 orders gives Hexaly two small choices to make instead of eight
    # chained operations to satisfy at once.
    lines = []
    for order in ORDERS:
        at_0, at_1 = Fraction(0), Fraction(1)
        for k in order:
            at_0, at_1 = OPERATIONS[k](at_0), OPERATIONS[k](at_1)
        slope = at_1 - at_0
        den = slope.denominator * at_0.denominator
        lines.append((int(slope * den), int(at_0 * den), den))
    num, add, den = (model.array([line[i] for line in lines]) for i in range(3))

    m = model.int(1, 150)  # my age in years
    h = model.int(1, 150)  # my husband's age in years
    to_husband = model.int(0, len(ORDERS) - 1)  # the order of operations that turns my age into his
    to_me = model.int(0, len(ORDERS) - 1)       # the order of operations that turns his age into mine

    # The first order applied to my age gives his age, and the second order applied to his age gives mine
    model.constraint(model.at(den, to_husband) * h == model.at(num, to_husband) * m + model.at(add, to_husband))
    model.constraint(model.at(den, to_me) * m == model.at(num, to_me) * h + model.at(add, to_me))
    # The two orders are different
    model.constraint(to_husband != to_me)

    return optimizer, {"m": m, "h": h}
