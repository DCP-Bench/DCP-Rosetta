"""Subset sum: how many bags of each kind were stolen so that the coins lost add up to the given total."""
import hexaly.optimizer as hx


def build(instance):
    # coin_numbers[i] = number of coins in one bag of kind i; total_coins_lost = coins lost in the theft altogether
    sizes, total = instance["coin_numbers"], instance["total_coins_lost"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # bags[i] = number of stolen bags of kind i (each holding sizes[i] coins).
    # Upper bound (derived): more than total // size such bags would hold more coins than were lost.
    bags = [model.int(0, total // size) for size in sizes]

    # The coins in the stolen bags add up to the total number of coins lost
    model.constraint(model.sum(size * b for size, b in zip(sizes, bags)) == total)

    return optimizer, {"bags": bags}
