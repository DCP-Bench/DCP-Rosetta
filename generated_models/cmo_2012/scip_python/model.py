# cmo_2012: a SCIP (Python) model from DCP Rosetta.
# Download the `cmo_2012.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cmo_2012.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python cmo_2012.py cmo_2012.json

from math import isqrt

from pyscipopt import Model


def create_model(instance):
    """Given positive integers a and b such that a - b is a prime number p and
    a * b is a perfect square n * n, find the smallest a that is at least min_a.
    Outputs: a, b, n and p."""
    min_a = instance["min_a"]      # the given minimum for a
    max_val = instance["max_val"]  # the instance's upper limit for a; the problem itself gives no bound

    model = Model("cmo_2012")

    # a: the first number, between min_a and max_val
    a = model.addVar("a", vtype="I", lb=min_a, ub=max_val)
    # b: the second number; the problem says b > 0, and b < a since a - b is a prime (at least 2)
    b = model.addVar("b", vtype="I", lb=1, ub=max_val)
    # n: the square root of a * b; since b >= 1 and b < a, 1 <= n < a <= max_val
    n = model.addVar("n", vtype="I", lb=1, ub=max_val)
    # p: the prime a - b, which is at least 2 and at most a, so at most max_val
    p = model.addVar("p", vtype="I", lb=2, ub=max_val)

    # Primality of p. SCIP has no primality constraint, so it is written as: p has no divisor d
    # with 2 <= d < p. A composite p <= max_val has a divisor d with d <= sqrt(p) <= sqrt(max_val),
    # so checking only the d up to isqrt(max_val) is enough.
    for d in range(2, isqrt(max_val) + 1):
        # q and r: the quotient and remainder with p = d * q + r, 0 <= r <= d - 1; q <= max_val // d
        q = model.addVar(f"q_{d}", vtype="I", lb=0, ub=max_val // d)
        r = model.addVar(f"r_{d}", vtype="I", lb=0, ub=d - 1)
        model.addCons(p == d * q + r)
        # g = 0 forces p <= d. So p > d forces g = 1, and then r >= 1: d does not divide p.
        # The indicator takes activeone=False because it is the case g = 0 that needs p <= d.
        g = model.addVar(f"g_{d}", vtype="B")
        model.addConsIndicator(p <= d, binvar=g, activeone=False)
        model.addCons(r >= g)

    # the difference of the two numbers is the prime p
    model.addCons(a - b == p)

    # a * b is the perfect square n * n (a nonlinear equality, which SCIP solves as such)
    model.addCons(a * b == n * n)

    # the objective: the smallest a that is at least min_a
    model.setObjective(a, "minimize")

    return model, {"a": a, "b": b, "n": n, "p": p}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
