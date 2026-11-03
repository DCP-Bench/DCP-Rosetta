# bin_packing: an Exact (Python) model from DCP Rosetta.
# Download the `bin_packing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python bin_packing.py bin_packing.json

from exact import Exact


def create_model(instance):
    """Assign each item to a bin so that the total weight of the items in each bin does not
    exceed the bin capacity."""
    weights = instance["weights"]    # weights[j]: the weight of item j
    capacity = instance["capacity"]  # the most weight a bin can hold
    num_bins = instance["num_bins"]  # the number of bins, numbered from 0

    n_items = len(weights)

    solver = Exact()

    # Exact identifies its variables by name.
    # bins[j] is the bin that item j goes into
    bins = [f"bin{j}" for j in range(n_items)]
    for name in bins:
        solver.addVariable(name, 0, num_bins - 1)

    # in_bin[j][i] is 1 when item j goes into bin i, and 0 when not
    in_bin = [[f"in_{j}_{i}" for i in range(num_bins)] for j in range(n_items)]
    for j in range(n_items):
        for i in range(num_bins):
            solver.addVariable(in_bin[j][i], 0, 1)

    # Each item goes into exactly one bin.
    for j in range(n_items):
        solver.addConstraint([(1, in_bin[j][i]) for i in range(num_bins)], True, 1, True, 1)

    # The bin number of each item is the bin it goes into.
    for j in range(n_items):
        solver.addConstraint([(i, in_bin[j][i]) for i in range(num_bins)] + [(-1, bins[j])],
                             True, 0, True, 0)

    # The items in each bin weigh no more than the capacity.
    for i in range(num_bins):
        solver.addConstraint([(weights[j], in_bin[j][i]) for j in range(n_items)],
                             False, 0, True, capacity)

    return solver, {"bins": bins}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
