from hermax.model import Model


def build(instance):
    # Archery puzzle: minimize absolute deviation from target score.
    # Find the number of hits on each target to get as close to target_score as possible.

    targets = instance["targets"]
    target_score = instance["target_score"]

    m = Model()

    n_targets = len(targets)
    if n_targets == 0:
        return m, {"hits": []}

    # Upper bound on hits per target
    min_target = min(targets)
    max_hits = (target_score // min_target) + max(targets) + 1 if min_target > 0 else target_score

    # Number of hits on each target
    hits = m.int_vector("hits", n_targets, 0, max_hits)

    # Total score
    total_score = sum(hits[i] * targets[i] for i in range(n_targets))

    # Minimize |total_score - target_score| using auxiliary variables and soft clauses.
    # Create auxiliary variable for deviation
    max_dev = target_score + max(targets) if targets else target_score
    deviation = m.int("deviation", 0, max_dev)

    # Constrain deviation to be at least the absolute difference
    m &= (deviation >= total_score - target_score)
    m &= (deviation >= target_score - total_score)

    # Minimize deviation: pay for each unit of deviation
    for d in range(1, min(101, max_dev + 1)):
        m.obj[1] += (deviation >= d)

    return m, {"hits": hits}
