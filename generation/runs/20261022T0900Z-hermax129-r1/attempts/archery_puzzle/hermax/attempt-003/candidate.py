from hermax.model import Model


def build(instance):
    targets = instance["targets"]
    target_score = instance["target_score"]

    m = Model()

    n_targets = len(targets)
    if n_targets == 0:
        return m, {"hits": []}

    # Upper bound on hits per target based on how many we'd need to reach target
    min_target = min(targets)
    max_hits = (target_score // min_target) + max(targets) + 1 if min_target > 0 else target_score

    # Hits on each target
    hits = m.int_vector("hits", n_targets, 0, max_hits)

    # Total score achieved
    total_score = sum(hits[i] * targets[i] for i in range(n_targets))

    # Minimize deviation from target_score.
    # Strategy: create a variable for the deviation and minimize it directly.

    max_possible_score = max_hits * sum(targets)

    # deviation variable: will represent |total_score - target_score|
    deviation = m.int("deviation", 0, max_possible_score)

    # Constrain deviation to be at least the absolute difference
    m &= (deviation >= total_score - target_score)
    m &= (deviation >= target_score - total_score)

    # Minimize deviation by paying for each unit
    # We enumerate small deviations and pay if we exceed them
    for d in range(1, min(150, max_possible_score + 1)):
        m.obj[1] += (deviation >= d)

    return m, {"hits": hits}
