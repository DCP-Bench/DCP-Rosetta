from hermax.model import Model


def build(instance):
    # Archery puzzle: minimize absolute deviation from target score.
    targets = instance["targets"]
    target_score = instance["target_score"]

    m = Model()

    n_targets = len(targets)
    if n_targets == 0:
        return m, {"hits": []}

    min_target = min(targets)
    max_target = max(targets)
    max_hits = (target_score // min_target) + max_target + 1 if min_target > 0 else target_score

    # Hits on each target
    hits = m.int_vector("hits", n_targets, 0, max_hits)
    total_score = sum(hits[i] * targets[i] for i in range(n_targets))

    # Minimize absolute deviation from target_score.
    # Strategy: use soft clauses that pay for deviations at each distance level.
    # For distance d, we pay 1 if the deviation is >= d.
    # Total cost = sum of (1 if deviation >= d) for d = 1..max_distance
    # This equals the deviation value itself.

    # Compute reasonable distance to check
    max_distance = min(200, target_score + sum(targets))

    # Add soft clauses: pay when total_score is outside the acceptable range
    # At distance d: scores in range [target_score - d, target_score + d] pay 0 for this level
    for d in range(1, max_distance + 1):
        # Pay 1 if deviation is at least d:
        # (total_score <= target_score - d) | (total_score >= target_score + d)
        too_far = m.bool(f"dev_ge_{d}")
        m &= (too_far == ((total_score <= target_score - d) | (total_score >= target_score + d)))
        m.obj[1] += too_far

    return m, {"hits": hits}
