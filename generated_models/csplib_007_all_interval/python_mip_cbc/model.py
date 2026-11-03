# csplib_007_all_interval: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_007_all_interval.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_007_all_interval.py csplib_007_all_interval.json

import mip


def create_model(instance):
    """Find an order of the pitch-classes 0 to n-1, each used once, in which the intervals
    between neighbouring notes are 1 to n-1, each occurring once."""
    n = instance["n"]  # the number of pitch-classes, and so of notes in the series

    model = mip.Model(solver_name="CBC")

    # p[i][v] is 1 when the note at position i has pitch-class v
    p = [[model.add_var(f"p_{i}_{v}", var_type=mip.BINARY) for v in range(n)]
         for i in range(n)]
    # x[i] is the pitch-class of the note at position i
    x = [model.add_var(f"x_{i}", lb=0, ub=n - 1, var_type=mip.INTEGER)
         for i in range(n)]

    # Each position holds exactly one pitch-class, and x[i] is that pitch-class.
    for i in range(n):
        model += mip.xsum(p[i]) == 1
        model += x[i] == mip.xsum(v * p[i][v] for v in range(n))
    # Each pitch-class occurs at exactly one position.
    for v in range(n):
        model += mip.xsum(p[i][v] for i in range(n)) == 1

    # slack: larger than any interval, so the condition for the direction not chosen always holds
    slack = 2 * (n - 1)
    # d[i] is the interval between the notes at positions i and i+1
    d = [model.add_var(f"d_{i}", lb=1, ub=n - 1, var_type=mip.INTEGER)
         for i in range(n - 1)]
    # s[i] is 1 when the note at position i+1 is below the note at position i, and 0 when it is above
    s = [model.add_var(f"s_{i}", var_type=mip.BINARY) for i in range(n - 1)]
    # The interval at position i is the distance between the two neighbouring notes.
    for i in range(n - 1):
        model += d[i] >= x[i + 1] - x[i]
        model += d[i] >= x[i] - x[i + 1]
        model += d[i] <= (x[i + 1] - x[i]) + slack * (1 - s[i])
        model += d[i] <= (x[i] - x[i + 1]) + slack * s[i]

    # q[i][k-1] is 1 when the interval at position i is k
    q = [[model.add_var(f"q_{i}_{k}", var_type=mip.BINARY) for k in range(1, n)]
         for i in range(n - 1)]
    # Each position has exactly one interval.
    for i in range(n - 1):
        model += mip.xsum(q[i]) == 1
        model += d[i] == mip.xsum(k * q[i][k - 1] for k in range(1, n))
    # Each interval from 1 to n-1 occurs at exactly one position.
    for k in range(1, n):
        model += mip.xsum(q[i][k - 1] for i in range(n - 1)) == 1

    return model, {"x": x, "diffs": d}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
