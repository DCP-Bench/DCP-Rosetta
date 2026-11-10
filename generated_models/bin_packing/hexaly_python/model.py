"""Bin packing: put each item into one of the bins so that no bin holds more weight than its capacity.

A satisfaction problem: there is no objective, any assignment within capacity is accepted.
"""
import hexaly.optimizer as hx


def build(instance):
    # weights[i]: weight of item i; capacity: the most weight any one bin can hold; num_bins: how many bins are available
    weights, capacity, num_bins = instance["weights"], instance["capacity"], instance["num_bins"]
    n = len(weights)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # bins[i] is the bin (0-indexed) that item i goes into
    # (the domain 0..num_bins-1 makes "each item in exactly one bin" hold by construction)
    bins = [model.int(0, num_bins - 1) for _ in range(n)]

    # The total weight of the items in each bin does not exceed the capacity
    # (the comparison bins[i] == b is 1 when item i is in bin b, so the sum is the load of bin b)
    for b in range(num_bins):
        model.constraint(model.sum(weights[i] * (bins[i] == b) for i in range(n)) <= capacity)

    return optimizer, {"bins": bins}
