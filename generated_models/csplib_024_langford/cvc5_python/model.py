# csplib_024_langford: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_024_langford.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_024_langford.py csplib_024_langford.json

import itertools

import cvc5.pythonic as c5


def create_model(instance):
    """Arrange two copies of each number from 1 to k into one sequence of 2k numbers, so that the
    two 1's appear one number apart, the two 2's two numbers apart, ..., and the two k's k numbers
    apart."""
    k = instance["k"]  # the largest number, of which the sequence holds two copies
    n = 2 * k          # the length of the sequence

    # The number at each place of the sequence, from 1 to k.
    sol = [c5.Int(f"sol_{p}") for p in range(n)]

    solver = c5.Solver()

    solver.add([c5.And(s >= 1, s <= k) for s in sol])

    # start[v, i] is true when the two copies of v stand at places i and i + v + 1.
    start = {}
    for v in range(1, k + 1):
        for i in range(n - v - 1):
            start[v, i] = c5.Bool(f"start_{v}_{i}")

    # Each number has exactly one place where its two copies stand.
    for v in range(1, k + 1):
        starts = [start[v, i] for i in range(n - v - 1)]
        solver.add(c5.Or(starts))
        solver.add([c5.Not(c5.And(a, b)) for a, b in itertools.combinations(starts, 2)])

    # The pairs with a copy of some number at place p.
    for p in range(n):
        covers = [start[v, p] for v in range(1, k + 1) if (v, p) in start]
        covers += [start[v, p - v - 1] for v in range(1, k + 1) if (v, p - v - 1) in start]
        # Every place of the sequence is taken by exactly one copy.
        solver.add(c5.Or(covers))
        solver.add([c5.Not(c5.And(a, b)) for a, b in itertools.combinations(covers, 2)])

    # A pair at places i and i + v + 1 puts the number v at both places.
    solver.add([c5.Implies(b, c5.And(sol[i] == v, sol[i + v + 1] == v))
                for (v, i), b in start.items()])

    return solver, {"sol": sol}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
