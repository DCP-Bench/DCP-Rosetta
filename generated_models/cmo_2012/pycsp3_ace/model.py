# cmo_2012: a PyCSP3 model from DCP Rosetta.
# Download the `cmo_2012.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cmo_2012.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python cmo_2012.py cmo_2012.json

from pycsp3 import *


def create_model(instance):
    """Given two positive integers a and b, where a - b is a prime number p and a * b is a
    perfect square n^2, find the smallest value of a no less than a given minimum min_a.
    Also b is larger than 0, and none of the four values a, b, n and p may exceed max_val."""
    min_a = instance["min_a"]  # the smallest value a may take, from the instance
    max_val = instance["max_val"]  # the largest value of a, b, n and p, from the instance

    # p is a prime no larger than max_val. The primes up to max_val are its domain; trial
    # division only builds that list.
    primes = [q for q in range(2, max_val + 1) if all(q % d for d in range(2, int(q ** 0.5) + 1))]
    # a * b is the square n * n with n at most max_val, so its value is one of these squares.
    perfect_squares = {k * k for k in range(1, max_val + 1)}

    # a: the first integer, at least min_a and at most max_val
    a = Var(dom=range(min_a, max_val + 1))
    # b: the second integer, larger than 0 and at most max_val
    b = Var(dom=range(1, max_val + 1))
    # n: the root of the perfect square a * b = n^2, at most max_val
    n = Var(dom=range(1, max_val + 1))
    # p: the prime a - b
    p = Var(dom=primes)
    # a_times_b: the perfect square a * b, which is also n * n. It is a separate variable
    # because ACE 2.6 accepts invalid tuples for a Product over four or more variables, and
    # a * b == n * n would be one such product over (a, b, n, n).
    a_times_b = Var(dom=perfect_squares)

    satisfy(
        # a - b is the prime p.
        a - b == p,
        # a * b is a perfect square.
        a * b == a_times_b,
        # The perfect square a * b is n * n.
        n * n == a_times_b,
    )

    # Minimise a, the smallest value of a that qualifies.
    minimize(a)

    return {"a": a, "b": b, "n": n, "p": p}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
