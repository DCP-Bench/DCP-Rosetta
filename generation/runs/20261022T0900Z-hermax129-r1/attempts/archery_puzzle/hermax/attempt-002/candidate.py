from hermax.model import Model


def build(instance):
    targets = instance["targets"]
    target_score = instance["target_score"]

    m = Model()

    n_targets = len(targets)
    if n_targets == 0:
        return m, {"hits": []}

    # Upper bound on hits per target
    min_target = min(targets)
    max_target = max(targets)
    max_hits = (target_score // min_target) + max_target + 1 if min_target > 0 else target_score

    # Number of hits on each target
    hits = m.int_vector("hits", n_targets, 0, max_hits)

    # Total score
    total_score = sum(hits[i] * targets[i] for i in range(n_targets))

    # Minimize |total_score - target_score| by minimizing the maximum of undershoot and overshoot.

    max_possible_score = max_hits * sum(targets) if targets else 0

    # Undershoot: amount below target (if total_score < target_score)
    undershoot = m.int("undershoot", 0, target_score)
    m &= (undershoot >= target_score - total_score)

    # Overshoot: amount above target (if total_score > target_score)
    overshoot = m.int("overshoot", 0, max_possible_score)
    m &= (overshoot >= total_score - target_score)

    # Deviation is the maximum of undershoot and overshoot
    deviation = m.max([undershoot, overshoot])

    # Minimize deviation using soft clauses.
    # For each unit of deviation, add a soft clause that fires when we exceed that unit.
    # Cost = sum of (1 if deviation < d else 0) for d = 1..max_dev
    # This means cost = min(deviation, max_dev)

    max_dev_to_consider = min(200, target_score + max(targets))

    for d in range(1, max_dev_to_consider + 1):
        # Pay 1 if deviation >= d (i.e., if we don't have a small enough deviation)
        m.obj[1] += (deviation >= d)

    return m, {"hits": hits}
