"""Equal-sum subsets: two disjoint non-empty subsets S and T of A with the same sum."""
import hexaly.optimizer as hx


def build(instance):
    # A = the given set of different integers; S and T are chosen among its elements
    a = instance["A"]
    n = len(a)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # in_S[i] = 1 if element a[i] is in S; in_T[i] = 1 if element a[i] is in T (both lists have the length of A)
    in_S = [model.bool() for _ in range(n)]
    in_T = [model.bool() for _ in range(n)]

    # The subsets are disjoint
    for i in range(n):
        model.constraint(in_S[i] + in_T[i] <= 1)
    # Both are non-empty
    model.constraint(model.sum(in_S) >= 1)
    model.constraint(model.sum(in_T) >= 1)
    # The sum of the elements in S equals the sum of the elements in T
    model.constraint(model.sum(a[i] * in_S[i] for i in range(n)) == model.sum(a[i] * in_T[i] for i in range(n)))

    return optimizer, {"in_S": in_S, "in_T": in_T}
