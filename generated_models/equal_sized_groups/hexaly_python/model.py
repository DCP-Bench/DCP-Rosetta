"""Equal-sized groups: split a sorted list into k groups at k - 1 break points, never between equal values,
so that the group sizes are as close to round(N / k) as possible."""
import hexaly.optimizer as hx


def build(instance):
    # a = the N element values of the sorted list (equal values may repeat); k = number of groups
    a, k = instance["a"], instance["k"]
    n = len(a)  # N, the number of elements
    target = round(n / k)  # the ideal group size, as the statement defines it
    # A break point p (1-based: the number of elements before the break) is allowed only where the
    # value changes, a[p - 1] != a[p], so that equal values stay in one group
    allowed = [p for p in range(1, n) if a[p - 1] != a[p]]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # The allowed break points as a Hexaly array, so that pick can index into it
    positions = model.array(allowed)
    # pick[j] = index, into the allowed break points, of the j-th break point. Choosing an index keeps
    # every break point on an allowed position.
    pick = [model.int(0, len(allowed) - 1) for _ in range(k - 1)]
    # The break points increase strictly, so none repeats and no group is empty
    for j in range(k - 2):
        model.constraint(pick[j] < pick[j + 1])
    # x[j] = the j-th break point, 1-based as the output asks: the number of elements before it
    x = [model.at(positions, p) for p in pick]

    # Group j runs from break point j to break point j + 1, with 0 and N as the outer ends;
    # sizes[j] = the number of elements in group j
    bounds = [0] + x + [n]
    sizes = [bounds[j + 1] - bounds[j] for j in range(k)]
    # error[j] is the distance of group j's size from the target size, at most N. It is bounded below
    # from both sides and minimised, so at the minimum it equals |sizes[j] - target|; linear, unlike abs()
    error = [model.int(0, n) for _ in range(k)]
    # The error of each group is at least its size minus the target, and at least the target minus its size
    for j in range(k):
        model.constraint(error[j] >= sizes[j] - target)
        model.constraint(error[j] >= target - sizes[j])

    # Minimise the total error: the sum over the groups of the distance between the group's size and round(N / K)
    model.minimize(model.sum(error))
    return optimizer, {"x": x}
