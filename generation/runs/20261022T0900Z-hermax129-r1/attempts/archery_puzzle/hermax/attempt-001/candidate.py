from hermax.model import Model


def build(instance):
    targets = instance["targets"]
    target_score = instance["target_score"]

    m = Model()

    n_targets = len(targets)

    if n_targets == 0:
        return m, {"hits": []}

    # Upper bound on max_hits per target
    # We need enough to potentially hit target_score
    min_target = min(targets)
    max_target = max(targets)
    max_hits = (target_score // min_target) + max_target + 1 if min_target > 0 else target_score

    # Number of hits on each target
    hits = m.int_vector("hits", n_targets, 0, max_hits)

    # Total score
    total_score = sum(hits[i] * targets[i] for i in range(n_targets))

    # Minimize absolute deviation from target_score.
    # Create auxiliary variables to represent deviations and minimize them.

    max_possible_score = max_hits * sum(targets) if targets else 0

    # under = max(0, target_score - total_score): undershoot
    under = m.int("under", 0, target_score)
    m &= (under >= target_score - total_score)
    m &= (under >= 0)

    # over = max(0, total_score - target_score): overshoot
    over = m.int("over", 0, max_possible_score)
    m &= (over >= total_score - target_score)
    m &= (over >= 0)

    # deviation = max(under, over)
    deviation = m.max([under, over])

    # Minimize deviation using soft clauses.
    # Pay for each unit of deviation above 0.
    max_dev_to_consider = min(100, max(target_score, sum(targets)))
    for d in range(1, max_dev_to_consider + 1):
        m.obj[1] += (deviation >= d)

    return m, {"hits": hits}
