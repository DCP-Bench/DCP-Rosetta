# bin_packing: a PyCSP3 model from DCP Rosetta.
# Download the `bin_packing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python bin_packing.py bin_packing.json

from pycsp3 import *


def create_model(instance):
    """Several items of given weights are put into a number of bins of a fixed
    capacity, each item in one bin, so that the total weight in each bin does not
    exceed the capacity. Find the bin of each item, numbered from 0."""
    weights = instance["weights"]      # weights[i]: the weight of item i
    capacity = instance["capacity"]    # the most weight a bin can hold
    num_bins = instance["num_bins"]    # the number of bins, numbered from 0
    n_items = len(weights)

    # bins[i] is the bin item i is put in
    bins = VarArray(size=n_items, dom=range(num_bins))

    satisfy(
        # The items in each bin weigh no more than the bin's capacity.
        BinPacking(bins, sizes=weights, limits=[capacity] * num_bins),
    )

    return {"bins": bins}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
