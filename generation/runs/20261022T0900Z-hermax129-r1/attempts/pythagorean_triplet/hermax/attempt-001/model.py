from hermax.model import Model

TOTAL = 1000  # the problem fixes a + b + c = 1000


def build(instance):
    m = Model()
    # Natural numbers a < b < c with a + b + c = 1000. Since a < b < c,
    # a is below a third of the total, b below a half and c below the total.
    a = m.int("a", 1, 332)
    b = m.int("b", 2, 499)
    c = m.int("c", 3, TOTAL - 3)

    m &= (a + 1 <= b)
    m &= (b + 1 <= c)
    m &= (a + b + c == TOTAL)

    # a^2 + b^2 = c^2, with each square written as a sum over its value.
    # Squares are reified over the small domains above rather than as wide
    # integers.
    a_sq = sum(k * k * (a == k) for k in range(a.lb, a.ub + 1))
    b_sq = sum(k * k * (b == k) for k in range(b.lb, b.ub + 1))
    c_sq = sum(k * k * (c == k) for k in range(c.lb, c.ub + 1))
    m &= (a_sq + b_sq == c_sq)

    return m, {"a": a, "b": b, "c": c}
