# csplib_049_number_partitioning: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_049_number_partitioning.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_049_number_partitioning.py csplib_049_number_partitioning.json

import mip


def create_model(instance):
    """Partition the numbers 1..n into two sets A and B of the same size, with the same sum
    and the same sum of squares."""
    n = instance["n"]      # the numbers 1..n are partitioned
    n_per_set = n // 2     # the size of each set

    model = mip.Model(solver_name="CBC")

    # a[k][j] is 1 when position k of A holds the number j + 1, and 0 when not.
    a = [[model.add_var(f"a_{k}_{j}", var_type=mip.BINARY) for j in range(n)] for k in range(n_per_set)]
    # b[k][j] is 1 when position k of B holds the number j + 1, and 0 when not.
    b = [[model.add_var(f"b_{k}_{j}", var_type=mip.BINARY) for j in range(n)] for k in range(n_per_set)]

    # Each position of A holds exactly one number.
    for k in range(n_per_set):
        model += mip.xsum(a[k]) == 1

    # Each position of B holds exactly one number.
    for k in range(n_per_set):
        model += mip.xsum(b[k]) == 1

    # Each number from 1 to n is in exactly one of A and B.
    for j in range(n):
        model += mip.xsum([a[k][j] for k in range(n_per_set)] + [b[k][j] for k in range(n_per_set)]) == 1

    # A and B have the same sum.
    model += (mip.xsum((j + 1) * a[k][j] for k in range(n_per_set) for j in range(n))
              == mip.xsum((j + 1) * b[k][j] for k in range(n_per_set) for j in range(n)))

    # A and B have the same sum of squares.
    model += (mip.xsum((j + 1) ** 2 * a[k][j] for k in range(n_per_set) for j in range(n))
              == mip.xsum((j + 1) ** 2 * b[k][j] for k in range(n_per_set) for j in range(n)))

    # The numbers of A and of B.
    outputs = {
        "A": [mip.xsum((j + 1) * a[k][j] for j in range(n)) for k in range(n_per_set)],
        "B": [mip.xsum((j + 1) * b[k][j] for j in range(n)) for k in range(n_per_set)],
    }
    return model, outputs


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
