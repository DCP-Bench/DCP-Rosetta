"""Production planning: maximise sum c[j] * X[j] subject to sum X[j] / a[j] <= b and 0 <= X[j] <= u[j]."""
from math import lcm

import hexaly.optimizer as hx


def build(instance):
    a, b, c, u = instance["a"], instance["b"], instance["c"], instance["u"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # X[j] between 0 and u[j]
    x = [model.int(0, uj) for uj in u]

    # sum X[j] / a[j] <= b, multiplied through by the lcm of the a[j] to stay in integers
    scale = lcm(*a)
    model.constraint(model.sum((scale // aj) * xj for aj, xj in zip(a, x)) <= scale * b)

    # Maximise the total profit
    total_profit = model.sum(cj * xj for cj, xj in zip(c, x))
    model.maximize(total_profit)
    return optimizer, {"x": x, "total_profit": total_profit}
