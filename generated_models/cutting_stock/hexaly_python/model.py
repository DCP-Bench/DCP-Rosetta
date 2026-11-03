"""Cutting stock: choose how often to cut each pattern so every width's orders are met with the fewest raw rolls."""
import hexaly.optimizer as hx


def build(instance):
    # orders[w] = number of rolls of width w that must be delivered;
    # pieces[p][w] = number of rolls of width w that one raw roll yields when cut with pattern p
    orders, pieces = instance["orders"], instance["num_rolls_width"]
    # num_patterns = number of cutting patterns; n_widths = number of widths to be cut (one order per width)
    n_patterns, n_widths = instance["num_patterns"], len(orders)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # patterns_used[p] = how many raw rolls are cut with pattern p.
    # Upper bound (derived): using a pattern more than max(orders) times is never needed, since
    # max(orders) uses already give each width it contains at least its order.
    patterns_used = [model.int(0, max(orders)) for _ in range(n_patterns)]

    # For each width, the total number of rolls cut meets its orders
    for w in range(n_widths):
        model.constraint(model.sum(pieces[p][w] * patterns_used[p] for p in range(n_patterns)) >= orders[w])

    # Minimise the total number of raw rolls cut (the sum over all patterns of the rolls cut with it)
    min_rolls_cut = model.sum(patterns_used)
    model.minimize(min_rolls_cut)
    return optimizer, {"patterns_used": patterns_used, "min_rolls_cut": min_rolls_cut}
