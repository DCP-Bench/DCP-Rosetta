# cmo_2012: a hermax (Python) model from DCP Rosetta.
# Download the `cmo_2012.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cmo_2012.html
# Then run it on the first instance (after `pip install hermax`):
#   python cmo_2012.py cmo_2012.json

import math

from hermax.model import Model


def _is_prime(k):
    # Plain trial division, used only to filter the candidate values of u before modelling.
    if k < 2:
        return False
    d = 2
    while d * d <= k:
        if k % d == 0:
            return False
        d += 1
    return True


def create_model(instance):
    """Given a minimum min_a and a bound max_val, find positive integers a, b, n, p such that
    a - b = p is prime, a * b = n * n, b > 0 and a >= min_a, with a as small as possible.
    Report a, b, n and p."""
    min_a = instance["min_a"]      # a must be at least this value
    max_val = instance["max_val"]  # every value is at most max_val; b, n, p are below a, so bounding a suffices

    # Derivation. Write a = s*u*u and b = s*v*v with s squarefree (a*b is a square).
    # Then a - b = s*(u-v)*(u+v). That is prime only when s = 1, u - v = 1 and u + v is prime,
    # so a = u*u, b = (u-1)*(u-1), n = u*(u-1) and p = 2u-1, with 2u-1 prime.
    # b > 0 needs u >= 2.

    # Smallest u with u*u >= min_a, and u >= 2 so that b > 0.
    lo = max(2, math.isqrt(max(min_a - 1, 0)) + 1)
    # Largest u with u*u <= max_val.
    hi = math.isqrt(max_val)

    # The admissible (u, a, b, n, p) rows: u in lo..hi with 2u-1 prime, computed before modelling.
    rows = [(k, k * k, (k - 1) * (k - 1), k * (k - 1), 2 * k - 1)
            for k in range(lo, hi + 1) if _is_prime(2 * k - 1)]

    m = Model()
    # u is the square root of a; a, b, n, p are the four quantities the problem reports.
    u = m.int("u", lo, hi)
    a = m.int("a", lo * lo, hi * hi)                  # a = u*u
    b = m.int("b", (lo - 1) ** 2, (hi - 1) ** 2)      # b = (u-1)*(u-1), positive
    n = m.int("n", lo * (lo - 1), hi * (hi - 1))      # n*n = a*b, so n = u*(u-1)
    p = m.int("p", 2 * lo - 1, 2 * hi - 1)            # p = a - b = 2u-1, must be prime

    # The quantities take values together as one admissible row: (u, a, b, n, p) is one of the rows.
    m &= m.table([u, a, b, n, p], allowed=rows)

    # Minimise a, the value the problem asks for.
    m.obj += a

    # The objective in the problem's terms: the value of a, the cost minimised above.
    return m, {"a": a, "b": b, "n": n, "p": p}, a


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
        print("objective =", result[objective])
    else:
        print("No solution:", result.status)
