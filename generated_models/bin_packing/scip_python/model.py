# bin_packing: a SCIP (Python) model from DCP Rosetta.
# Download the `bin_packing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python bin_packing.py bin_packing.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Bin packing: put every item into one of the bins so that the total weight
    of the items in each bin does not exceed the bin's capacity. This is a
    satisfaction problem, so any assignment that fits is an answer."""
    # weights[i]: the weight of item i; the number of items is taken from the data
    weights = instance["weights"]
    # capacity: the most weight that one bin can hold
    capacity = instance["capacity"]
    # num_bins: how many bins there are, numbered 0 to num_bins - 1
    num_bins = instance["num_bins"]

    n = len(weights)
    model = Model("bin_packing")

    # x[i, b] is 1 when item i is put in bin b, and 0 when not
    x = model.addMatrixVar((n, num_bins), vtype="B", name="x")

    # Each item is put in exactly one bin: each row of x has a single 1.
    model.addMatrixCons(x.sum(axis=1) == 1)

    # The items in each bin weigh no more than the bin's capacity.
    for b in range(num_bins):
        model.addCons(quicksum(weights[i] * x[i, b] for i in range(n)) <= capacity)

    # bins[i]: the bin item i is put in, 0-indexed. With exactly one x[i, b] equal
    # to 1 in each row, this sum is that bin's number. It is an expression, not a
    # new integer variable, because x already determines it.
    bins = [quicksum(b * x[i, b] for b in range(num_bins)) for i in range(n)]

    return model, {"bins": bins}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
