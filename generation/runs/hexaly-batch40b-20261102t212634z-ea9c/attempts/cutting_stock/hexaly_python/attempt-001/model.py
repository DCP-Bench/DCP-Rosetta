"""Cutting stock: choose how often to cut each pattern so every width's orders are met with the fewest raw rolls."""
import hexaly.optimizer as hx


def build(instance):
    orders, pieces = instance["orders"], instance["num_rolls_width"]  # pieces[p][w]: rolls of width w per pattern p
    n_patterns, n_widths = instance["num_patterns"], len(orders)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # patterns_used[p] is how many raw rolls are cut with pattern p; no pattern is needed more
    # often than the largest order
    patterns_used = [model.int(0, max(orders)) for _ in range(n_patterns)]

    # For each width, the rolls cut meet its orders
    for w in range(n_widths):
        model.constraint(model.sum(pieces[p][w] * patterns_used[p] for p in range(n_patterns)) >= orders[w])

    # Minimise the number of raw rolls cut
    min_rolls_cut = model.sum(patterns_used)
    model.minimize(min_rolls_cut)
    return optimizer, {"patterns_used": patterns_used, "min_rolls_cut": min_rolls_cut}
