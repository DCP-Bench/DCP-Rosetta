"""CMO 2012: positive a, b with a - b = p prime and a * b = n^2; the smallest a no less than min_a."""
import hexaly.optimizer as hx


def build(instance):
    # min_a = the smallest value a may take; max_val = the upper limit on every value, a search limit from the instance
    min_a, top = instance["min_a"], instance["max_val"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # The four unknowns, each at most max_val: a is at least min_a, b is positive (the statement
    # requires it), n is the root of the perfect square a * b (n^2 = a * b <= max_val^2, so n <= max_val),
    # p is the prime a - b, so at least 2
    a = model.int(max(1, min_a), top)  # a, the value to minimise
    b = model.int(1, top)  # b, a positive integer
    n = model.int(1, top)  # n, with a * b = n^2
    p = model.int(2, top)  # p, the prime a - b

    # a - b is the prime p, and a * b is the perfect square n^2
    model.constraint(a - b == p)
    model.constraint(a * b == n * n)
    # p is prime: a composite p has a divisor d with 2 <= d <= sqrt(p) <= sqrt(max_val), so no d in
    # that range may divide p, unless p is d itself
    d = 2
    while d * d <= top:
        model.constraint(model.or_(p == d, p % d != 0))
        d += 1

    # Implied by the statement, added to give Hexaly a bound: gcd(a, b) divides the prime a - b, and gcd = p would
    # make ab/p^2 = (b/p)(b/p + 1) a square, impossible for b > 0. So a and b are coprime
    # with a square product, hence squares themselves: a = s^2, b = t^2, and
    # (s - t)(s + t) = p forces s = t + 1.
    s = model.int(1, top)  # s, the square root of a
    t = model.int(1, top)  # t, the square root of b
    # a and b are the squares of s and t, which differ by one
    model.constraint(a == s * s)
    model.constraint(b == t * t)
    model.constraint(s == t + 1)

    # The smallest a no less than min_a: minimise a
    model.minimize(a)
    return optimizer, {"a": a, "b": b, "n": n, "p": p}
