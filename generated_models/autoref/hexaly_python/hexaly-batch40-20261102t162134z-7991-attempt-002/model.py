"""Autoref: a series s_0..s_{n+1} where each i in 0..n occurs exactly s_i times, and s_{n+1} = m."""
import hexaly.optimizer as hx


def build(instance):
    n, m = instance["n"], instance["m"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # takes[j][v] = 1 if s_j equals v, for j in 0..n. Each s_j counts the occurrences of a
    # value 0..n and so lies in 0..n; Booleans with linear sums.
    takes = [[model.bool() for _ in range(n + 1)] for _ in range(n + 1)]
    for j in range(n + 1):
        model.constraint(model.sum(takes[j]) == 1)
    s = [model.sum(v * takes[j][v] for v in range(n + 1)) for j in range(n + 1)]

    # Each i from 0 to n occurs exactly s_i times in the series, the last entry m included
    for i in range(n + 1):
        model.constraint(model.sum(takes[j][i] for j in range(n + 1)) + (1 if m == i else 0) == s[i])

    # The last entry is m
    return optimizer, {"s": s + [m]}
