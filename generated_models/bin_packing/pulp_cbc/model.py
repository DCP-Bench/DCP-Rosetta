# bin_packing: a PuLP (Python) model from DCP Rosetta.
# Download the `bin_packing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python bin_packing.py bin_packing.json

import pulp


def create_model(instance):
    """Assign each item to a bin so that the items in each bin weigh no more than the bin's
    capacity. Each item goes into exactly one bin."""
    weights = instance["weights"]    # weights[j]: the weight of item j
    capacity = instance["capacity"]  # the most weight a bin can hold
    num_bins = instance["num_bins"]  # the number of bins, numbered from 0
    items = range(len(weights))      # the item numbers

    problem = pulp.LpProblem("bin_packing", pulp.LpMinimize)

    # bins[j] is the bin that item j goes into
    bins = [pulp.LpVariable(f"bin_{j}", 0, num_bins - 1, cat="Integer") for j in items]
    # in_bin[j][i] is 1 when item j goes into bin i
    in_bin = [[pulp.LpVariable(f"in_{j}_{i}", cat="Binary") for i in range(num_bins)]
              for j in items]

    # Each item goes into exactly one bin, and bins[j] is that bin.
    for j in items:
        problem += pulp.lpSum(in_bin[j]) == 1
        problem += bins[j] == pulp.lpSum(i * in_bin[j][i] for i in range(num_bins))

    # The items in each bin weigh no more than the capacity.
    for i in items:
        if i < num_bins:
            problem += pulp.lpSum(weights[j] * in_bin[j][i] for j in items) <= capacity

    return problem, {"bins": bins}


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
