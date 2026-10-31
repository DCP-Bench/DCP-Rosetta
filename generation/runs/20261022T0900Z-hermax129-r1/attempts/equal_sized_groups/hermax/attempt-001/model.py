from hermax.model import Model


def build(instance):
    a = instance["a"]
    k = instance["k"]
    n = len(a)

    # Target group size: round(N/K)
    target = round(n / k)

    m = Model()

    # x[i] are the K-1 break points (1-based indices where to split)
    x = m.int_vector("x", k - 1, 1, n - 1)

    # Break points must be strictly increasing
    m &= x.increasing()

    # Can only break between elements with different values
    # (elements with same value must stay in the same group)
    for i in range(k - 1):
        # x[i] is 1-based index of break point
        # We break after position x[i]-1 (0-based), so a[x[i]-1] != a[x[i]]
        m &= (a[x[i] - 1] != a[x[i]])

    # Compute group sizes
    sizes = m.int_vector("size", k, 1, n)
    m &= (sizes[0] == x[0])
    for i in range(1, k - 1):
        m &= (sizes[i] == x[i] - x[i - 1])
    m &= (sizes[k - 1] == n - x[k - 2])

    # Minimize total error: sum of |size[i] - target|
    # For each group i, add a penalty equal to the absolute error from target
    # We use auxiliary variables error[i] that satisfy:
    # error[i] >= size[i] - target  and  error[i] >= target - size[i]
    # Minimizing this makes it equal to |size[i] - target|
    for i in range(k):
        error = m.int("error_" + str(i), 0, n)
        m &= (error >= sizes[i] - target)
        m &= (error >= target - sizes[i])
        m.obj[1] += error

    return m, {"x": x}
