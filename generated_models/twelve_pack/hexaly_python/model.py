"""Twelve pack: packs of different sizes that meet or exceed the target with as few surplus items as possible."""
import hexaly.optimizer as hx


def build(instance):
    packs, target = instance["packs"], instance["target"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # counts[i] is the number of packs of size packs[i]; more than the target needs would only add items
    counts = [model.int(0, target // size + 1) for size in packs]

    # The packs hold at least the target number of items
    items = model.sum(size * c for size, c in zip(packs, counts))
    model.constraint(items >= target)

    # The closest combination: the fewest items in total
    model.minimize(items)
    return optimizer, {"counts": counts}
