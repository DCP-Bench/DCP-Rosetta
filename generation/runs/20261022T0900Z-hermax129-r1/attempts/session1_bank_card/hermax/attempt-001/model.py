from hermax.model import Model


def build(instance):
    m = Model()
    # The PIN is four digits a, b, c, d.
    digits = m.int_vector("digit", 4, 0, 9)
    a, b, c, d = digits[0], digits[1], digits[2], digits[3]

    # No two digits are the same.
    m &= digits.all_different()

    # The 2-digit numbers ab, bc, cd and da are all two digits, so the leading digits are non-zero.
    m &= (a >= 1)
    m &= (b >= 1)
    m &= (c >= 1)
    m &= (d >= 1)

    # The 2-digit number cd is 3 times the 2-digit number ab.
    m &= (10 * c + d == 3 * (10 * a + b))

    # The 2-digit number da is 2 times the 2-digit number bc.
    m &= (10 * d + a == 2 * (10 * b + c))

    return m, {"a": a, "b": b, "c": c, "d": d}
