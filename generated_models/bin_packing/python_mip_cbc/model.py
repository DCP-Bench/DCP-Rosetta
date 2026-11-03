# bin_packing: a Python-MIP (Python) model from DCP Rosetta.
# Download the `bin_packing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python bin_packing.py bin_packing.json

import mip


def create_model(instance):
    """Assign each item to one of the bins, each with a fixed capacity, so that the total
    weight of the items in each bin does not exceed the capacity. The result gives the bin
    of each item, numbered from 0."""
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight a bin can hold
    num_bins = instance["num_bins"]  # the number of bins available
    n_items = len(weights)           # the number of items

    model = mip.Model(solver_name="CBC")

    # in_bin[i][b] is 1 when item i goes into bin b, and 0 when not
    in_bin = [[model.add_var(f"in_bin_{i}_{b}", var_type=mip.BINARY)
               for b in range(num_bins)]
              for i in range(n_items)]
    # bins[i] is the number of the bin that item i goes into
    bins = [model.add_var(f"bins_{i}", lb=0, ub=num_bins - 1, var_type=mip.INTEGER)
            for i in range(n_items)]

    # Each item goes into exactly one bin.
    for i in range(n_items):
        model.add_constr(mip.xsum(in_bin[i]) == 1)

    # The items in each bin weigh no more than the capacity.
    for b in range(num_bins):
        model.add_constr(mip.xsum(weights[i] * in_bin[i][b] for i in range(n_items)) <= capacity)

    # The bin number of each item is the bin it goes into.
    for i in range(n_items):
        model.add_constr(bins[i] == mip.xsum(b * in_bin[i][b] for b in range(num_bins)))

    return model, {"bins": bins}


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
