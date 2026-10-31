from hermax.model import Model


def build(instance):
    # The sorted list and the number of groups come from the instance.
    a = instance["a"]
    k = instance["k"]
    n = len(a)

    # Target group size: round(N / K), as in the description.
    target = round(n / k)

    model = Model()

    # Break points x_1 .. x_{K-1}: x_g is the 1-based index of the last element of
    # group g. Points are strictly increasing, so every group is non-empty.
    x = model.int_vector("x", k - 1, 1, n - 1)
    for g in range(k - 2):
        model &= (x[g] < x[g + 1])

    # A break may only fall between two elements with different values, since
    # equal values must stay in the same group. Split after element p (1-based)
    # is forbidden when a[p-1] == a[p].
    for g in range(k - 1):
        for p in range(1, n):
            if a[p - 1] == a[p]:
                model &= x[g].forbid_value(p)

    # Points with the group ends: 0 before the first group, n after the last one.
    points = [0] + list(x) + [n]

    # Each group's size is S_g = points[g+1] - points[g]. The error is |S_g - target|,
    # written with two one-sided slacks per group: over >= S - T and under >= T - S.
    objective = 0
    for g in range(k):
        size = points[g + 1] - points[g]
        over = model.int(f"over_{g}", 0, n)
        under = model.int(f"under_{g}", 0, n)
        model &= (over >= size - target)
        model &= (under >= target - size)
        objective = objective + over + under

    # Minimise the total error over all groups.
    model.obj += objective

    return model, {"x": x}
