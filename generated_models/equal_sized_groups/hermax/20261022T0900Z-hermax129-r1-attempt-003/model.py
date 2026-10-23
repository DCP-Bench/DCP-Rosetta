from hermax.model import Model


def build(instance):
    a = instance["a"]
    k = instance["k"]
    n = len(a)
    target = round(n / k)

    m = Model()

    # x[i] is the 1-based index of the last element of group i (i = 0 .. k-2).
    # A break point lies between elements 1 .. n-1.
    x = m.int_vector("x", k - 1, 1, n - 1)

    # Break points strictly increase, so every group is non-empty.
    for i in range(k - 2):
        m &= (x[i + 1] - x[i] >= 1)

    # Equal values must share a group: a break after element v (1-based) is
    # only allowed where a[v-1] and a[v] differ.
    for v in range(1, n):
        if a[v - 1] == a[v]:
            for i in range(k - 1):
                m &= x[i].forbid_value(v)

    # Group sizes: size g is the distance between consecutive break points,
    # with the first group starting at 0 and the last ending at n. Each size
    # is a bounded integer tied to its linear expression.
    sizes = []
    for g in range(k):
        s = m.int(f"size_{g}", 1, n)
        if g == 0:
            m &= (s == x[0])
        elif g == k - 1:
            m &= (s == n - x[k - 2])
        else:
            m &= (s == x[g] - x[g - 1])
        sizes.append(s)

    # Minimise the absolute deviation of each size from round(n / k), written
    # as the ladder literals of the size variable: |s - t| counts the values
    # k <= t with s < k, plus the values k > t with s >= k. Each literal is
    # soft with weight 1 and costs 1 when it is true (m.obj += lit minimises).
    for s in sizes:
        for kk in range(s.lb + 1, s.ub + 1):
            if kk <= target:
                m.obj += 1 * (s < kk)
            else:
                m.obj += 1 * (s >= kk)

    return m, {"x": x}
