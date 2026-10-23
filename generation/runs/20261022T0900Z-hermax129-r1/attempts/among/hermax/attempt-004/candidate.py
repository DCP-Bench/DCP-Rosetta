from functools import reduce
import operator

from hermax.model import Model


def build(instance):
    n = instance["n"]
    count = instance["m"]
    v = instance["v"]

    # Fixed constant of the problem: every entry of x lies in 0..7.
    VALUE_LO, VALUE_HI = 0, 7

    m = Model()
    x = m.int_vector("x", n, VALUE_LO, VALUE_HI)

    # in_v[i] is true exactly when x[i] takes one of the values in v.
    # x[i] == val is a Literal, so each direction is a clause over Literals.
    in_v = m.bool_vector("in_v", n)
    for i in range(n):
        # x[i] == val  implies  in_v[i]
        for val in v:
            m &= (~(x[i] == val)) | in_v[i]
        # in_v[i]  implies  x[i] equals some value in v
        if v:
            any_match = reduce(operator.or_, [x[i] == val for val in v])
            m &= (~in_v[i]) | any_match
        else:
            m &= ~in_v[i]

    # Exactly `count` entries of x take a value from v.
    m &= (sum(in_v[i] for i in range(n)) == count)

    return m, {"x": x}
