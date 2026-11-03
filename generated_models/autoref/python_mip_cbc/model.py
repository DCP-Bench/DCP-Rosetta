# autoref: a Python-MIP (Python) model from DCP Rosetta.
# Download the `autoref.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python autoref.py autoref.json

import mip


def create_model(instance):
    """Find a series s[0], s[1], ..., s[n+1] in which each value i from 0 to n occurs
    exactly s[i] times, and whose last element s[n+1] equals m."""
    n = instance["n"]  # the largest value counted in the series
    m = instance["m"]  # the required last element of the series

    model = mip.Model(solver_name="CBC")

    n_positions = n + 2  # the series has n + 2 elements
    max_value = max(n, m)  # the largest value any element can take

    # s[j] is the element at position j.
    s = [model.add_var(f"s_{j}", lb=0, ub=(n if j <= n else m), var_type=mip.INTEGER)
         for j in range(n_positions)]
    # x[j][v] is 1 when the element at position j is v, and 0 otherwise.
    x = [[model.add_var(f"x_{j}_{v}", var_type=mip.BINARY) for v in range(max_value + 1)]
         for j in range(n_positions)]

    # Each position holds exactly one value, and s[j] is that value.
    for j in range(n_positions):
        model += mip.xsum(x[j][v] for v in range(max_value + 1)) == 1
        model += s[j] == mip.xsum(v * x[j][v] for v in range(max_value + 1))

    # The value i occurs exactly s[i] times in the series, for each i from 0 to n.
    for i in range(n + 1):
        model += s[i] == mip.xsum(x[j][i] for j in range(n_positions))

    # The last element is m.
    model += s[n + 1] == m

    return model, {"s": s}


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
