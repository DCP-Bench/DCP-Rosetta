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

    # With c = 1000 - a - b, a^2 + b^2 = c^2 becomes
    # a*b - 1000*a - 1000*b + 500000 = 0. Fixing a = k gives a linear
    # equation in b: b * (1000 - k) = 500000 - 1000 * k.
    for k in range(a.lb, a.ub + 1):
        m &= (b * (TOTAL - k) == 500000 - TOTAL * k).only_if(a == k)

    return m, {"a": a, "b": b, "c": c}
