"""Hanging weights: integer weights 1..13 (A to M) that balance every bar of the diagram, a bar hanging from
another counting as one weight equal to its total.

Each bar balances about its pivot: the weights on one side, times their distances in diagram units, equal those
on the other side.
"""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    names = "abcdefghijklm"
    w = {name: model.int(1, 13) for name in names}
    a, b, c, d, e, f, g, h, i, j, k, l, m = (w[n] for n in names)

    # Total weight of each hanging bar, with everything below it
    ef = e + f                  # the bar holding E and F
    left = h + i + ef           # the bar holding H and I, with the E-F bar
    top_left = l + m + left     # the bar holding L and M, with the left bar
    ab = a + b                  # the bottom bar with A and B
    cd = c + d                  # the bottom right bar with C and D
    gcd = g + cd                # the bar holding G, with the C-D bar
    right = j + k + ab + gcd    # the bar holding J and K, with the A-B bar and the G bar

    # The bottom right bar: C is 5 units from the pivot and D is 1 unit
    model.constraint(5 * c == d)
    # The bar above it: G is 3 units from the pivot and the C-D bar is 2 units
    model.constraint(3 * g == 2 * cd)
    # The A-B bar: A is 4 units from the pivot and B is 1 unit
    model.constraint(4 * a == b)
    # The E-F bar: E is 3 units from the pivot and F is 2 units
    model.constraint(3 * e == 2 * f)
    # The bar holding H and I: H is 3 units left of the pivot; the E-F bar 2 units and I 3 units right
    model.constraint(3 * h == 2 * ef + 3 * i)
    # The bar holding L and M: the left bar is 1 unit left of the pivot; L is 1 unit and M 4 units right
    model.constraint(left == l + 4 * m)
    # The bar holding J and K: the A-B bar 3 units and J 2 units left of the pivot; K 1 unit and the G bar 2 units right
    model.constraint(3 * ab + 2 * j == k + 2 * gcd)
    # The top bar: its left end is 4 units from the hook and its right end 3 units
    model.constraint(4 * top_left == 3 * right)

    return optimizer, w
