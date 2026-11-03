"""Twelve pack: packs of different sizes that meet or exceed the target with as few surplus items as possible."""
import hexaly.optimizer as hx


def build(instance):
    # packs[i] = size of pack type i (items in one pack); target = number of items to reach
    packs, target = instance["packs"], instance["target"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # counts[i] = number of packs of size packs[i] that are bought.
    # Upper bound (derived): target // size + 1 packs of one size already reach the target,
    # so more would only add surplus items.
    counts = [model.int(0, target // size + 1) for size in packs]

    # The combination meets or exceeds the target: the packs hold at least target items in total
    items = model.sum(size * c for size, c in zip(packs, counts))
    model.constraint(items >= target)

    # The closest combination: with at least target items required, the fewest items in total
    # is the smallest surplus over the target
    model.minimize(items)
    return optimizer, {"counts": counts}
