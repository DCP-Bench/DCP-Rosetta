"""
Bin packing: assign items to bins respecting capacity constraint.

Each item must be assigned to exactly one bin, such that the total
weight of items in each bin does not exceed the bin capacity.
"""

from hermax.model import Model


def build(instance):
    m = Model()

    weights = instance["weights"]
    capacity = instance["capacity"]
    num_bins = instance["num_bins"]
    num_items = len(weights)

    # Variable: bin assignment for each item (0 to num_bins-1)
    bins = m.int_vector("bins", num_items, 0, num_bins - 1)

    # Capacity constraint: total weight in each bin <= capacity
    for b in range(num_bins):
        # Sum of weights for items assigned to bin b
        # (bins[i] == b) returns a Literal that is true iff item i is in bin b
        m &= (sum(weights[i] * (bins[i] == b) for i in range(num_items)) <= capacity)

    return m, {"bins": bins}
