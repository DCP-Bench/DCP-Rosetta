"""Fifty puzzle: knock over dummies whose numbers add up to exactly the target sum."""
import hexaly.optimizer as hx


def build(instance):
    values, target = instance["values"], instance["target_sum"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # dummies[i] = 1 if dummy i is knocked over
    dummies = [model.bool() for _ in values]

    # The numbers on the knocked-over dummies add up to the target, neither more nor less
    model.constraint(model.sum(v * d for v, d in zip(values, dummies)) == target)
    return optimizer, {"dummies": dummies}
