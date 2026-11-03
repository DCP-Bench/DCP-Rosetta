"""Equal-sized groups: split a sorted list into k groups at k - 1 break points, never between equal values,
so that the group sizes are as close to round(N / k) as possible."""
import hexaly.optimizer as hx


def build(instance):
    a, k = instance["a"], instance["k"]
    n = len(a)
    target = round(n / k)  # the ideal group size, as the statement defines it
    # A break after (1-based) position p is allowed only where the value changes, so that equal
    # values stay in one group
    allowed = [p for p in range(1, n) if a[p - 1] != a[p]]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # pick[j] chooses the j-th break among the allowed positions; the breaks increase
    positions = model.array(allowed)
    pick = [model.int(0, len(allowed) - 1) for _ in range(k - 1)]
    for j in range(k - 2):
        model.constraint(pick[j] < pick[j + 1])
    x = [model.at(positions, p) for p in pick]

    # The group sizes, from the first element to the last
    bounds = [0] + x + [n]
    sizes = [bounds[j + 1] - bounds[j] for j in range(k)]
    # error[j] is at least the distance of group j's size from the target, both ways, so at the
    # minimum it equals it; linear, unlike abs()
    error = [model.int(0, n) for _ in range(k)]
    for j in range(k):
        model.constraint(error[j] >= sizes[j] - target)
        model.constraint(error[j] >= target - sizes[j])

    # Minimise the total error
    model.minimize(model.sum(error))
    return optimizer, {"x": x}
