# bin_packing: a Z3 (Python) model from DCP Rosetta.
# Download the `bin_packing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python bin_packing.py bin_packing.json

import z3


def create_model(instance):
    """Assign each item to a bin so that the total weight of the items in each bin does
    not exceed the bin capacity."""
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight a bin can hold
    num_bins = instance["num_bins"]  # the number of bins, numbered from 0

    # bins[i]: the bin that item i goes into
    bins = [z3.Int(f"bin_{i}") for i in range(len(weights))]

    solver = z3.Solver()

    # Each item goes into one of the bins.
    solver.add([z3.And(0 <= b, b <= num_bins - 1) for b in bins])

    # The items in each bin weigh no more than the capacity.
    for k in range(num_bins):
        solver.add(z3.Sum([z3.If(b == k, w, 0) for w, b in zip(weights, bins)]) <= capacity)

    return solver, {"bins": bins}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
