from hermax.model import Model


def build(instance):
    A = instance["A"]
    n = len(A)

    m = Model()
    in_S = m.bool_vector("S", n)
    in_T = m.bool_vector("T", n)

    # S and T are disjoint: no element is in both.
    for i in range(n):
        m &= (~in_S[i] | ~in_T[i])

    # S and T are non-empty.
    m &= in_S.at_least_one()
    m &= in_T.at_least_one()

    # The sum of the elements in S equals the sum of the elements in T.
    m &= (sum(A[i] * in_S[i] for i in range(n)) == sum(A[i] * in_T[i] for i in range(n)))

    return m, {"in_S": in_S, "in_T": in_T}
