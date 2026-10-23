from math import isqrt

from hermax.model import Model

# The problem's given set (fixed constants of the problem): the product of x and any member
# of the set, plus one, must be a perfect square.
GIVEN = [1, 3, 8, 120]


def build(instance):
    max_val = instance["max_val"]

    m = Model()
    # The fifth number, between 0 and max_val.
    x = m.int("number", 0, max_val)

    for a in GIVEN:
        # a * x + 1 is a perfect square: a * x + 1 == s * s for some root s.
        # The root is bounded by the largest value a * x + 1 can take.
        R = isqrt(a * max_val + 1)
        root = m.int(f"root_{a}", 0, R)
        for s in range(R + 1):
            t = s * s - 1
            if t < 0 or t % a:
                # no integer x gives a * x + 1 == s * s for this root
                m &= (root != s)
            else:
                # root s forces x to the value that makes a * x + 1 equal s * s
                m &= (x == t // a).only_if(root == s)

    return m, {"number": x}
