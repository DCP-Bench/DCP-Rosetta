"""CMO 2012: positive a, b with a - b = p prime and a * b = n^2; the smallest a no less than min_a."""
import hexaly.optimizer as hx


def build(instance):
    min_a, top = instance["min_a"], instance["max_val"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Every value lies between 1 and max_val; a is at least min_a
    a = model.int(max(1, min_a), top)
    b = model.int(1, top)
    n = model.int(1, top)
    p = model.int(2, top)

    # a - b is the prime p, and a * b is the perfect square n^2
    model.constraint(a - b == p)
    model.constraint(a * b == n * n)
    # p is prime: no d from 2 up to sqrt(max_val) divides it, unless p is d itself
    d = 2
    while d * d <= top:
        model.constraint(model.or_(p == d, p % d != 0))
        d += 1

    # Implied, to give Hexaly a bound: gcd(a, b) divides the prime a - b, and gcd = p would
    # make ab/p^2 = (b/p)(b/p + 1) a square, impossible for b > 0. So a and b are coprime
    # with a square product, hence squares themselves: a = s^2, b = t^2, and
    # (s - t)(s + t) = p forces s = t + 1.
    s = model.int(1, top)
    t = model.int(1, top)
    model.constraint(a == s * s)
    model.constraint(b == t * t)
    model.constraint(s == t + 1)

    # The smallest such a
    model.minimize(a)
    return optimizer, {"a": a, "b": b, "n": n, "p": p}
