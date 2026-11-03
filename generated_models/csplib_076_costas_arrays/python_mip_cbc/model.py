# csplib_076_costas_arrays: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_076_costas_arrays.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_076_costas_arrays.py csplib_076_costas_arrays.json

import mip


def create_model(instance):
    """Place n marks on an n-by-n grid, one per row and one per column, so that the
    n(n-1)/2 vectors between the marks are all different (a Costas array)."""
    n = instance["n"]         # size of the grid, and the number of marks
    values = range(1, n + 1)  # the columns of the grid

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # at[i][v - 1] is 1 when the mark in row i is in column v, and 0 when not
    at = [[model.add_var(f"at_{i}_{v}", var_type=mip.BINARY) for v in values] for i in range(n)]

    # Each row has exactly one mark.
    for i in range(n):
        model += mip.xsum(at[i]) == 1

    # Each column has exactly one mark.
    for k in range(n):
        model += mip.xsum(at[i][k] for i in range(n)) == 1

    # For each distance l between rows and each column difference d, gap[i] is forced
    # to 1 when the marks in rows i and i + l are d columns apart. Marks in different
    # rows are never in the same column, so d = 0 is left out.
    for l in range(1, n):
        for d in range(-(n - 1), n):
            if d == 0:
                continue
            # gap[i] for each starting row i
            gap = {}
            for i in range(n - l):
                # (v, w): the columns of a pair of marks d columns apart on the grid
                pairs = [(v, v + d) for v in values if 1 <= v + d <= n]
                if not pairs:
                    continue
                gap[i] = model.add_var(f"gap_{l}_{d}_{i}", lb=0, ub=1)
                for v, w in pairs:
                    model += gap[i] >= at[i][v - 1] + at[i + l][w - 1] - 1

            # At most one pair of marks l rows apart is d columns apart.
            if len(gap) > 1:
                model += mip.xsum(gap.values()) <= 1

    # costas[i] is the column of the mark in row i
    costas = [model.add_var(f"X_{i}", lb=1, ub=n, var_type=mip.INTEGER) for i in range(n)]
    for i in range(n):
        model += costas[i] == mip.xsum(v * at[i][v - 1] for v in values)

    return model, {"costas": costas}


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
