# bin_packing: a CPMpy model from DCP Rosetta.
# Download the `bin_packing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python bin_packing.py bin_packing.json

import cpmpy as cp


def create_model(instance):
    """Assign each item to a bin so that the total weight of the items in each bin does
    not exceed the bin capacity."""
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight a bin can hold
    num_bins = instance["num_bins"]  # the number of bins available

    # bins[i] is the bin that item i is assigned to, numbered from 0
    bins = cp.intvar(0, num_bins - 1, shape=len(weights), name="bins")

    model = cp.Model()
    # The items in each bin weigh no more than the capacity.
    for b in range(num_bins):
        model.add(cp.sum((bins == b) * weights) <= capacity)

    return model, {"bins": bins}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
