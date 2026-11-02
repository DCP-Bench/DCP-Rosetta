# bin_packing: a cvc5 (Python) model from DCP Rosetta.
# Download the `bin_packing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python bin_packing.py bin_packing.json

import cvc5.pythonic as c5


def create_model(instance):
    """Assign each item to one of several bins, each of a fixed capacity, so that the total
    weight of the items in each bin does not exceed the capacity."""
    weights = instance["weights"]    # weights[k]: the weight of item k
    capacity = instance["capacity"]  # the most weight one bin can hold
    n_bins = instance["num_bins"]    # the number of bins available

    # bins[k]: the bin that item k goes into
    bins = [c5.Int(f"bin_{k}") for k in range(len(weights))]

    solver = c5.Solver()

    # Each item goes into one of the bins, numbered 0 to n_bins - 1.
    solver.add([c5.And(b >= 0, b <= n_bins - 1) for b in bins])

    # The items in each bin weigh no more than the capacity.
    for b in range(n_bins):
        solver.add(
            c5.Sum([c5.If(bin_k == b, w, 0) for bin_k, w in zip(bins, weights)]) <= capacity
        )

    return solver, {"bins": bins}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
