"""Autoref: a series s_0..s_{n+1} where each i in 0..n occurs exactly s_i times, and s_{n+1} = m."""
import hexaly.optimizer as hx


def build(instance):
    # n: the values counted are 0..n and the series is s_0..s_{n+1}; m: the required last entry s_{n+1}
    n, m = instance["n"], instance["m"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # takes[j][v] = 1 if entry s_j of the series equals v, for j and v in 0..n: each entry is limited to
    # the values 0..n that the series counts. One-hot Booleans make each count of occurrences a linear sum.
    takes = [[model.bool() for _ in range(n + 1)] for _ in range(n + 1)]
    # each entry s_j takes exactly one value
    for j in range(n + 1):
        model.constraint(model.sum(takes[j]) == 1)
    # s[j] is the value of entry s_j, a linear expression in takes (not a new decision)
    s = [model.sum(v * takes[j][v] for v in range(n + 1)) for j in range(n + 1)]

    # Each i from 0 to n occurs exactly s_i times in the series, the last entry m included
    # (that entry is fixed, so it adds 1 occurrence of the value m only)
    for i in range(n + 1):
        model.constraint(model.sum(takes[j][i] for j in range(n + 1)) + (1 if m == i else 0) == s[i])

    # The last entry s_{n+1} is m: appended as a constant to the series that is returned
    return optimizer, {"s": s + [m]}
