"""Subset sum: how many bags of each kind were stolen so that the coins lost add up to the given total."""
import hexaly.optimizer as hx


def build(instance):
    sizes, total = instance["coin_numbers"], instance["total_coins_lost"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # bags[i] is the number of stolen bags holding sizes[i] coins; no more than total // size fit the loss
    bags = [model.int(0, total // size) for size in sizes]

    # The coins in the stolen bags add up to the total lost
    model.constraint(model.sum(size * b for size, b in zip(sizes, bags)) == total)

    return optimizer, {"bags": bags}
