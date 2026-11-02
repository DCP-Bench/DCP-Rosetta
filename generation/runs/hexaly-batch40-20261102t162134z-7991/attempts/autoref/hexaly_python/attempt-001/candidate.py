"""Autoref: a series s_0..s_{n+1} where each i in 0..n occurs exactly s_i times, and s_{n+1} = m."""
import hexaly.optimizer as hx


def build(instance):
    n, m = instance["n"], instance["m"]
    length = n + 2
    # Every entry is a count of occurrences in the series (at most its length) or m itself
    top = max(length, m)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # takes[j][v] = 1 if s_j equals v; Booleans with linear sums
    takes = [[model.bool() for _ in range(top + 1)] for _ in range(length)]
    for j in range(length):
        model.constraint(model.sum(takes[j]) == 1)
    s = [model.sum(v * takes[j][v] for v in range(top + 1)) for j in range(length)]

    # Each i from 0 to n occurs exactly s_i times in the series
    for i in range(n + 1):
        model.constraint(model.sum(takes[j][i] for j in range(length)) == s[i])
    # The last entry is m
    model.constraint(s[n + 1] == m)

    return optimizer, {"s": s}
