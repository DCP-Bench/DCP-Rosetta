# csplib_084_hadamard_matrix: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_084_hadamard_matrix.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_084_hadamard_matrix.py csplib_084_hadamard_matrix.json

import math

import pulp


def create_model(instance):
    """Find two sequences a and b of odd length l, with entries -1 or +1, that each sum to 1
    and whose periodic autocorrelations add up to -2 at every shift s = 1, ..., (l-1)/2
    (a Legendre pair, which gives a Hadamard matrix)."""
    l = instance["l"]         # length of each sequence, an odd positive integer
    n_shifts = (l - 1) // 2   # number of shifts s = 1, ..., n_shifts that are constrained

    problem = pulp.LpProblem("hadamard_legendre_pairs", pulp.LpMinimize)  # satisfaction: no objective

    # p[name][i] is 1 when entry i of sequence name is +1, and 0 when it is -1
    p = {name: [pulp.LpVariable(f"{name}_{i}", cat="Binary") for i in range(l)] for name in ["a", "b"]}

    # Each sequence has (l + 1) / 2 entries +1, so its entries sum to 1.
    for name in ["a", "b"]:
        problem += pulp.lpSum(p[name]) == (l + 1) // 2

    # differ[(name, s, i)] marks a sign change between entries i and i + s (mod l) of sequence name.
    differ = {}
    # half_differ[(name, s)] is half the number of sign changes at shift s.
    half_differ = {}
    for s in range(1, n_shifts + 1):
        # Going once around a cycle of shifts, the sign changes an even number of times, so the
        # number of sign changes at shift s is even. Each cycle has odd length, so at least one
        # pair in it agrees, which bounds the number of sign changes by l - gcd(s, l).
        cap = (l - math.gcd(s, l)) // 2
        for name in ["a", "b"]:
            half_differ[(name, s)] = pulp.LpVariable(f"half_differ_{name}_{s}", 0, cap, cat="Integer")
            for i in range(l):
                j = (i + s) % l
                differ[(name, s, i)] = pulp.LpVariable(f"differ_{name}_{s}_{i}", cat="Binary")
                # differ is 1 exactly when the two entries have different signs.
                problem += differ[(name, s, i)] >= p[name][i] - p[name][j]
                problem += differ[(name, s, i)] >= p[name][j] - p[name][i]
                problem += differ[(name, s, i)] <= p[name][i] + p[name][j]
                problem += differ[(name, s, i)] <= 2 - p[name][i] - p[name][j]
            # The sign changes at shift s are twice half_differ.
            problem += pulp.lpSum(differ[(name, s, i)] for i in range(l)) == 2 * half_differ[(name, s)]

        # The two sequences together have l + 1 sign changes at shift s, so their periodic
        # autocorrelations add up to -2.
        problem += half_differ[("a", s)] + half_differ[("b", s)] == (l + 1) // 2

    # The reported entries are -1 or +1.
    outputs = {name: [2 * x - 1 for x in p[name]] for name in ["a", "b"]}
    return problem, outputs


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
