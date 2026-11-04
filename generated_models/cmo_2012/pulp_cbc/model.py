# cmo_2012: a PuLP (Python) model from DCP Rosetta.
# Download the `cmo_2012.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cmo_2012.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python cmo_2012.py cmo_2012.json

import math

import pulp


def primes_below(limit):
    """The primes p with 2 <= p < limit."""
    is_candidate = [True] * max(limit, 2)  # False once a number is known to be composite
    found = []  # the primes below limit, in increasing order
    for candidate in range(2, limit):
        if is_candidate[candidate]:
            found.append(candidate)
            for multiple in range(candidate * candidate, limit, candidate):
                is_candidate[multiple] = False
    return found


def create_model(instance):
    """Find two positive whole numbers a and b, with b at least 1, such that the
    difference a - b is a prime p and the product a * b is a perfect square n * n.
    Find the smallest such a that is at least min_a. Every value of a, b, n and p
    is at most max_val."""
    min_a = instance["min_a"]      # the smallest value a may take
    max_val = instance["max_val"]  # the largest value a, b, n and p may take

    problem = pulp.LpProblem("cmo_2012", pulp.LpMinimize)

    # a is the larger number
    a = pulp.LpVariable("a", min_a, max_val, cat="Integer")
    # b is the smaller number
    b = pulp.LpVariable("b", 1, max_val, cat="Integer")
    # n is the square root of a * b
    n = pulp.LpVariable("n", 0, max_val, cat="Integer")
    # p is the prime difference a - b
    p = pulp.LpVariable("p", 2, max_val, cat="Integer")

    # The smallest a.
    problem += a

    # is_p[q] is 1 when p is the prime q.
    prime_list = primes_below(max_val)
    is_p = {q: pulp.LpVariable(f"is_p_{q}", cat="Binary") for q in prime_list}
    # Exactly one prime below max_val is p.
    problem += pulp.lpSum(is_p.values()) == 1
    problem += p == pulp.lpSum(q * var for q, var in is_p.items())

    # p is the difference a - b.
    problem += p == a - b

    # Let g be the largest number dividing both a and b, and write a = g * x and
    # b = g * y, where x and y share no factor. Since a * b is a square, x and y are
    # both squares: x = s * s and y = t * t with s > t >= 1. The difference
    # g * (s - t) * (s + t) is prime only when g = 1, s - t = 1 and s + t = p.
    # So a = s * s, b = (s - 1) * (s - 1), n = s * (s - 1) and p = 2 * s - 1, for
    # some s from 2 up to the square root of max_val.
    top = math.isqrt(max_val)
    # is_s[s] is 1 when s is the chosen root.
    is_s = {s: pulp.LpVariable(f"is_s_{s}", cat="Binary") for s in range(2, top + 1)}
    # Exactly one root s is chosen, and a, b, n and p follow from it.
    problem += pulp.lpSum(is_s.values()) == 1
    problem += a == pulp.lpSum(s * s * var for s, var in is_s.items())
    problem += b == pulp.lpSum((s - 1) ** 2 * var for s, var in is_s.items())
    problem += n == pulp.lpSum(s * (s - 1) * var for s, var in is_s.items())
    problem += p == pulp.lpSum((2 * s - 1) * var for s, var in is_s.items())

    return problem, {"a": a, "b": b, "n": n, "p": p}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
