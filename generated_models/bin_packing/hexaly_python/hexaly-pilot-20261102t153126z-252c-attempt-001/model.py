"""Bin packing: put each item into one of the bins so that no bin holds more weight than its capacity."""
import hexaly.optimizer as hx


def build(instance):
    weights, capacity, num_bins = instance["weights"], instance["capacity"], instance["num_bins"]
    n = len(weights)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # bins[i] is the bin (0-indexed) that item i goes into
    bins = [model.int(0, num_bins - 1) for _ in range(n)]

    # The items in a bin weigh at most its capacity
    for b in range(num_bins):
        model.constraint(model.sum(weights[i] * (bins[i] == b) for i in range(n)) <= capacity)

    return optimizer, {"bins": bins}
