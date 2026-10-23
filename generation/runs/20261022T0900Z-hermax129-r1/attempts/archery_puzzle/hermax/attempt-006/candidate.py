from hermax.model import Model


def build(instance):
    # Archery: choose a nonnegative hit count per ring so that the total score is as
    # close as possible to target_score. Objective: minimise |total - target_score|.
    targets = list(instance["targets"])
    goal = instance["target_score"]
    n = len(targets)

    m = Model()
    if n == 0:
        return m, {"hits": []}

    # Bound on each count. If the total exceeded goal + max(targets), removing one arrow
    # would move the total closer to goal, so no optimal solution has a larger total.
    total_cap = goal + max(targets)
    upper = total_cap // min(targets)
    width = max(1, upper.bit_length())

    hits = m.int_vector("hits", n, 0, upper)

    # Channel each count to binary Booleans once; the weighted total is written over bits.
    bits = []
    for i in range(n):
        b = m.bool_vector(f"hit_bit{i}", width)
        expr = sum(2 ** k * b[k] for k in range(width))
        m &= (hits[i] == expr)
        bits.append(expr)

    total = sum(targets[i] * bits[i] for i in range(n))
    max_total = sum(targets[i] * upper for i in range(n))

    # |total - goal| as two one-sided slacks. Both are minimised linearly with m.obj += ...
    # (minimise polarity: the slack's value is the cost).
    over = m.int("over", 0, max(0, max_total - goal))
    under = m.int("under", 0, goal)
    m &= (over >= total - goal)
    m &= (under >= goal - total)
    m.obj += over + under

    return m, {"hits": hits}
