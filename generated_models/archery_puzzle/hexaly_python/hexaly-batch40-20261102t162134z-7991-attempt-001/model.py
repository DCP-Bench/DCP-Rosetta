"""Archery puzzle: hit the targets any number of times so that the score comes as close as possible to the target score."""
import hexaly.optimizer as hx


def build(instance):
    targets, goal = instance["targets"], instance["target_score"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # hits[i] is the number of arrows on target i. A closest score is below goal + max(targets):
    # from there, removing any arrow comes closer. So no target needs more hits than that bound.
    top = goal + max(targets)
    hits = [model.int(0, top // t) for t in targets]

    # Minimise the distance between the score and the target score
    score = model.sum(t * h for t, h in zip(targets, hits))
    model.minimize(model.abs(score - goal))
    return optimizer, {"hits": hits}
