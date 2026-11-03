"""Archery puzzle: hit the targets any number of times so that the score comes as close as possible to the target score."""
import hexaly.optimizer as hx


def build(instance):
    # targets[i] = points for one arrow on target i; target_score = the total score to come close to
    targets, goal = instance["targets"], instance["target_score"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Upper bound on the hits, derived here: some closest score is below goal + max(targets), because
    # from that score upward, removing one arrow gets closer to the goal. So target i never needs more
    # than (goal + max(targets)) // targets[i] hits.
    top = goal + max(targets)
    # hits[i] = number of arrows she puts on target i (any number, from 0 up to the bound above)
    hits = [model.int(0, top // t) for t in targets]

    # The total score: the points of each target times the arrows on it
    score = model.sum(t * h for t, h in zip(targets, hits))
    # Minimise the distance between the total score and the target score
    model.minimize(model.abs(score - goal))
    return optimizer, {"hits": hits}
