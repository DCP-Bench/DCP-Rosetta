# cmo_2012: an Exact (Python) model from DCP Rosetta.
# Download the `cmo_2012.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cmo_2012.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python cmo_2012.py cmo_2012.json

from math import isqrt

from exact import Exact


def create_model(instance):
    """Given two positive integers a and b, where a - b is a prime number and a * b is
    a perfect square n * n, find the smallest value of a no less than a given minimum.
    Also, b should be larger than 0."""
    min_a = instance["min_a"]      # the smallest value a may take
    max_val = instance["max_val"]  # the largest value any of the numbers may take

    # The primes below max_val, the possible values of a - b, found by sieving out the multiples of each prime.
    is_prime = [True] * max_val
    is_prime[0:2] = [False, False]
    for i in range(2, isqrt(max_val) + 1):
        if is_prime[i]:
            for multiple in range(i * i, max_val, i):
                is_prime[multiple] = False
    primes = [i for i in range(max_val) if is_prime[i]]

    # Two numbers have a square product exactly when they share the same square-free part s:
    # a = s * k * k and b = s * j * j, and then n = s * k * j. Listing these pairs in advance
    # is faster than multiplying the unknowns.
    # square_free[m] is m with every square factor divided out
    square_free = list(range(max_val + 1))
    for d in range(2, isqrt(max_val) + 1):
        for m in range(d * d, max_val + 1, d * d):
            while square_free[m] % (d * d) == 0:
                square_free[m] //= d * d
    # members[s] is the numbers from 1 to max_val whose square-free part is s, in increasing order
    members = {}
    for m in range(1, max_val + 1):
        members.setdefault(square_free[m], []).append(m)
    # triples lists every (a, b, n) with min_a <= a <= max_val, 1 <= b <= a and a * b = n * n
    triples = []
    for s, group in members.items():
        for ia, a in enumerate(group):
            if a < min_a:
                continue
            k = isqrt(a // s)
            for b in group[:ia + 1]:
                triples.append((a, b, s * k * isqrt(b // s)))

    solver = Exact()

    # Exact identifies its variables by name.
    # a is the larger number and b the smaller, both positive; n is the square root of a * b;
    # p is the prime a - b.
    solver.addVariable("a", min_a, max_val)
    solver.addVariable("b", 1, max_val)
    solver.addVariable("n", 0, max_val)
    solver.addVariable("p", 2, max_val)

    # a is at least b.
    solver.addConstraint([(1, "a"), (-1, "b")], True, 0)

    # chosen[i] is 1 when triple i is the pair (a, b, n) of the solution.
    chosen = [f"triple_{i}" for i in range(len(triples))]
    for name in chosen:
        solver.addVariable(name, 0, 1)

    # Exactly one triple is chosen, and a, b and n take its values.
    solver.addConstraint([(1, name) for name in chosen], True, 1, True, 1)
    for position, unknown in enumerate(("a", "b", "n")):
        solver.addConstraint([(triple[position], name) for triple, name in zip(triples, chosen)]
                             + [(-1, unknown)], True, 0, True, 0)

    # p is the difference a - b.
    solver.addConstraint([(1, "a"), (-1, "b"), (-1, "p")], True, 0, True, 0)

    # is_p[q] is 1 when p is the prime q.
    is_p = {q: f"p_is_{q}" for q in primes}
    for name in is_p.values():
        solver.addVariable(name, 0, 1)

    # p is one of the primes below max_val: exactly one prime is marked, and p is that prime.
    solver.addConstraint([(1, name) for name in is_p.values()], True, 1, True, 1)
    solver.addConstraint([(q, name) for q, name in is_p.items()] + [(-1, "p")], True, 0, True, 0)

    # by_difference[d] is the chosen flags of the triples whose a - b is d.
    by_difference = {}
    for triple, name in zip(triples, chosen):
        by_difference.setdefault(triple[0] - triple[1], []).append(name)

    # The chosen triple has difference a - b, which is p. If the difference is a prime q,
    # the chosen triple has difference q only when p is q. Any other difference is never chosen.
    for difference, names in by_difference.items():
        same_difference = [(1, name) for name in names]
        if difference in is_p:
            solver.addConstraint(same_difference + [(-1, is_p[difference])], True, 0, True, 0)
        else:
            solver.addConstraint(same_difference, False, 0, True, 0)

    # Smallest a.
    solver.setObjective([(1, "a")], minimize=True)

    return solver, {"a": "a", "b": "b", "n": "n", "p": "p"}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
