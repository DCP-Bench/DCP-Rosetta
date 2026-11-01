from math import lcm

from hermax.model import Model


def build(instance):
    a = instance["a"]
    b = instance["b"]
    c = instance["c"]
    u = instance["u"]
    n = len(a)

    # Scale the time constraint sum(X[j] / a[j]) <= b by L = lcm(a) so every
    # coefficient is an integer: sum((L // a[j]) * X[j]) <= b * L.
    L = lcm(*a)
    time_weight = [L // a[j] for j in range(n)]
    time_budget = b * L

    m = Model()

    # Production quantities: integers from 0 to u[j].
    max_u = max(u)
    X = m.int_vector("x", n, 0, max_u)
    for j in range(n):
        m &= (X[j] <= u[j])

    # The weighted time sum has large coefficients, so channel each quantity to
    # bits before writing the weighted constraint over them.
    bits_per = max(1, max_u.bit_length())
    bit_expr = []
    for j in range(n):
        bits = m.bool_vector(f"xb{j}", bits_per)
        expr = sum(2 ** k * bits[k] for k in range(bits_per))
        m &= (X[j] == expr)
        bit_expr.append(expr)

    # The total time spent must not exceed the available time b.
    m &= (sum(time_weight[j] * bit_expr[j] for j in range(n)) <= time_budget)

    # Maximise total profit, sum(c[j] * X[j]), by minimising its negation.
    total_profit = sum(c[j] * X[j] for j in range(n))
    m.obj += 0 - total_profit

    return m, {"x": X, "total_profit": total_profit}
