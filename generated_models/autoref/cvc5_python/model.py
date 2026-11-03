# autoref: a cvc5 (Python) model from DCP Rosetta.
# Download the `autoref.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python autoref.py autoref.json

import cvc5.pythonic as c5


def create_model(instance):
    """Find a series s[0], s[1], ..., s[n+1] in which each number i from 0 to n occurs
    exactly s[i] times, and whose last entry s[n+1] equals m."""
    n = instance["n"]  # the numbers 0 to n are counted in the series
    m = instance["m"]  # the required last entry of the series

    # s[k] is the k-th entry of the series
    s = [c5.Int(f"s{k}") for k in range(n + 2)]

    # Linear integer logic: cvc5 solves this model much faster than with the default Solver().
    solver = c5.SolverFor("QF_LIA")

    # Each count s[i] for i from 0 to n lies between 0 and n.
    for i in range(n + 1):
        solver.add(s[i] >= 0, s[i] <= n)

    # The last entry is m.
    solver.add(s[n + 1] == m)

    # The number i occurs exactly s[i] times in the series, for each i from 0 to n.
    for i in range(n + 1):
        solver.add(c5.Sum([c5.If(s[k] == i, 1, 0) for k in range(n + 2)]) == s[i])

    # The counts of 0 to n add up to the number of entries that lie between 0 and n.
    solver.add(
        c5.Sum([s[i] for i in range(n + 1)])
        == c5.Sum([c5.If(s[k] <= n, 1, 0) for k in range(n + 2)])
    )

    # Each number times its count adds up to the entries that lie between 0 and n.
    solver.add(
        c5.Sum([i * s[i] for i in range(n + 1)])
        == c5.Sum([c5.If(s[k] <= n, s[k], 0) for k in range(n + 2)])
    )

    return solver, {"s": s}


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
