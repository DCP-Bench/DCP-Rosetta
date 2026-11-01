import math

from hermax.model import Model


def _is_prime(k):
    # Fixed arithmetic helper, not part of the problem data.
    if k < 2:
        return False
    d = 2
    while d * d <= k:
        if k % d == 0:
            return False
        d += 1
    return True


def build(instance):
    min_a = instance["min_a"]
    max_val = instance["max_val"]

    # Derivation: a*b = n^2 means a = s*u^2 and b = s*v^2 for one squarefree s.
    # Then a - b = s*(u-v)*(u+v). That is prime only when s = 1, u - v = 1 and
    # u + v = p. So a = u^2, b = (u-1)^2, n = u*(u-1), p = 2u - 1 with p prime.
    # b > 0 gives u >= 2. The bounds use min_a (a >= min_a) and max_val (a <= max_val).
    lo = max(2, math.isqrt(max(min_a - 1, 0)) + 1)   # smallest u with u*u >= min_a
    hi = math.isqrt(max_val)                          # largest u with u*u <= max_val

    m = Model()
    u = m.int("u", lo, hi)

    # p = 2u - 1 must be prime: forbid the values of u where 2u - 1 is composite.
    for k in range(lo, hi + 1):
        if not _is_prime(2 * k - 1):
            m &= (u != k)

    # Minimise a = u*u; u is monotone in a, so minimising u is the same objective.
    m.obj += u

    # Outputs as linear sums over the indicator literals (u == k), one of which is true.
    a = sum(k * k * (u == k) for k in range(lo, hi + 1))
    b = sum((k - 1) * (k - 1) * (u == k) for k in range(lo, hi + 1))
    n = sum(k * (k - 1) * (u == k) for k in range(lo, hi + 1))
    p = sum((2 * k - 1) * (u == k) for k in range(lo, hi + 1))

    return m, {"a": a, "b": b, "n": n, "p": p}
