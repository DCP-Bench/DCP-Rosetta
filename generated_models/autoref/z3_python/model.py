# autoref: a Z3 (Python) model from DCP Rosetta.
# Download the `autoref.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python autoref.py autoref.json

import z3


def create_model(instance):
    """Find a series s[0], s[1], ..., s[n+1] in which every integer i from 0 to n
    occurs exactly s[i] times, and whose last element s[n+1] equals m."""
    n = instance["n"]  # the values 0 to n are counted in the series
    m = instance["m"]  # the required value of the last element

    # s[k] is the k-th element of the series
    s = [z3.Int(f"s_{k}") for k in range(n + 2)]

    solver = z3.Solver()

    # Every element of the series is a value from 0 to n.
    solver.add([z3.And(0 <= x, x <= n) for x in s])

    # The last element is m.
    solver.add(s[n + 1] == m)

    # The value i occurs exactly s[i] times in the series, for every i from 0 to n.
    solver.add([z3.Sum([z3.If(s[k] == i, 1, 0) for k in range(n + 2)]) == s[i]
                for i in range(n + 1)])

    # The counts of the values 0 to n add up to the length n + 2 of the series.
    solver.add(z3.Sum(s[: n + 1]) == n + 2)
    # Each value times its count adds up to the same total as the series.
    solver.add(z3.Sum([i * s[i] for i in range(n + 1)]) == z3.Sum(s))

    return solver, {"s": s}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
