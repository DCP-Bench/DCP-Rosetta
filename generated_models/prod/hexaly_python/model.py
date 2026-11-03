"""Production planning: maximise sum c[j] * X[j] subject to sum X[j] / a[j] <= b and 0 <= X[j] <= u[j]."""
from math import lcm

import hexaly.optimizer as hx


def build(instance):
    # a[j] = the divisor of X[j] in the limit constraint, sum X[j] / a[j] <= b; b = that limit;
    # c[j] = profit per unit of X[j]; u[j] = upper bound on X[j]
    a, b, c, u = instance["a"], instance["b"], instance["c"], instance["u"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[j] = the production quantity X[j] for j, an integer between 0 and u[j]
    x = [model.int(0, uj) for uj in u]

    # The sum of X[j] / a[j] is at most b. Both sides are multiplied by the lcm of the a[j], which
    # turns every coefficient lcm / a[j] into an integer, so the test is exact, with no fractions.
    scale = lcm(*a)
    model.constraint(model.sum((scale // aj) * xj for aj, xj in zip(a, x)) <= scale * b)

    # Maximise the total profit, the sum of c[j] * X[j]
    total_profit = model.sum(cj * xj for cj, xj in zip(c, x))
    model.maximize(total_profit)
    return optimizer, {"x": x, "total_profit": total_profit}
