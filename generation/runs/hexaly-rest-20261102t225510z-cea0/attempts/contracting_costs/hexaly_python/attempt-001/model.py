"""Contracting costs: the charge of each of six workmen, given what pairs of them are paid."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Each man's charge in whole dollars; none is paid more than the largest pair total
    charges = {name: model.int(0, 5300) for name in
               ("paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason")}

    # The pairs the contractor has to pay, and what they get together
    for (a, b), total in {("paper_hanger", "painter"): 1100, ("painter", "plumber"): 1700,
                          ("plumber", "electrician"): 1100, ("electrician", "carpenter"): 3300,
                          ("carpenter", "mason"): 5300, ("mason", "painter"): 3200}.items():
        model.constraint(charges[a] + charges[b] == total)

    return optimizer, charges
