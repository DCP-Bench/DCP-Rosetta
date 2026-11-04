# bin_packing: a hermax (Python) model from DCP Rosetta.
# Download the `bin_packing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Then run it on the first instance (after `pip install hermax`):
#   python bin_packing.py bin_packing.json

from hermax.model import Model


def create_model(instance):
    """Bin packing: assign each item to one bin so that the total weight of the
    items in every bin does not exceed the bin capacity. Satisfaction problem:
    any feasible assignment is an answer."""
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the weight a single bin can hold
    num_bins = instance["num_bins"]  # how many bins are available, numbered 0..num_bins-1
    n = len(weights)                 # the number of items

    m = Model()

    # bins[i] is the bin item i is put in, a number from 0 to num_bins - 1
    bins = m.int_vector("bins", n, 0, num_bins - 1)

    # Every bin holds at most its capacity: the weights of the items whose bin is b
    # add up to no more than the capacity, for each bin b.
    for b in range(num_bins):
        m &= (sum(weights[i] * (bins[i] == b) for i in range(n)) <= capacity)

    return m, {"bins": bins}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
