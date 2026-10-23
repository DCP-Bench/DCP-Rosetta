from hermax.model import Model


def build(instance):
    d = instance["denominations"]
    max_amount = instance["max_amount_to_pay"]
    n = len(d)

    # Every amount from 1 to max_amount - 1 must be payable.
    top = max_amount - 1

    # A count of coin j above top // d[j] never helps pay an amount <= top,
    # so this bound keeps the optimum reachable.
    ub = [top // dj for dj in d]

    m = Model()
    x = m.int_vector("x", n, 0, max(ub) if ub else 0)

    # Number of coins of each denomination used.
    for j in range(n):
        m &= (x[j] <= ub[j])

    # Each amount a is paid with y[j] coins of denomination j, where y[j] never
    # exceeds the coins bought (x[j]) and the amounts sum exactly to a.
    for a in range(1, max_amount):
        terms = []
        for j, dj in enumerate(d):
            if dj > a:
                continue
            y = m.int(f"y_{a}_{j}", 0, a // dj)
            m &= (y <= x[j])
            terms.append(dj * y)
        m &= (sum(terms) == a)

    # Minimise the total number of coins used.
    m.obj += sum(x[j] for j in range(n))

    return m, {"x": x}
