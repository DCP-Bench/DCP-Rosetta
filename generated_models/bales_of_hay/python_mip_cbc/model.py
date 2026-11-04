# bales_of_hay: a Python-MIP (Python) model from DCP Rosetta.
# Download the `bales_of_hay.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python bales_of_hay.py bales_of_hay.json

import mip


def create_model(instance):
    """Find the whole-number weight of each of n bales. The bales were weighed in every
    combination of two, and the pair weights were written down in numerical order,
    without saying which pair gave which weight."""
    n = instance["n"]              # the number of bales
    weights = instance["weights"]  # the weight of each pair of bales, as written down

    # The pairs of different bales, as (i, j) with i < j.
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    n_pairs = len(pairs)

    # The lightest and heaviest written weights.
    wmin = min(weights)
    wmax = max(weights)

    # With three or more bales, a bale is half of one pair plus another pair minus a third.
    # Each pair weighs between wmin and wmax, so each bale lies between lo and hi.
    lo = (2 * wmin - wmax) // 2
    hi = (2 * wmax - wmin) // 2

    model = mip.Model(solver_name="CBC")

    # bales[i] is the weight of bale i.
    bales = [model.add_var(f"bale_{i}", lb=lo, ub=hi, var_type=mip.INTEGER) for i in range(n)]

    # assign[p][k] is 1 when the k-th written weight is the weight of pairs[p], and 0 otherwise.
    assign = [[model.add_var(f"assign_{p}_{k}", var_type=mip.BINARY) for k in range(n_pairs)]
              for p in range(n_pairs)]

    # Each pair of bales has exactly one written weight.
    for p in range(n_pairs):
        model += mip.xsum(assign[p][k] for k in range(n_pairs)) == 1

    # Each written weight belongs to exactly one pair of bales.
    for k in range(n_pairs):
        model += mip.xsum(assign[p][k] for p in range(n_pairs)) == 1

    # The two bales of a pair weigh the written weight assigned to that pair.
    for p, (i, j) in enumerate(pairs):
        model += bales[i] + bales[j] == mip.xsum(weights[k] * assign[p][k] for k in range(n_pairs))

    return model, {"bales": bales}


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
