from hermax.model import Model


def build(instance):
    # Binary sequence s_i in {-1, +1} of length n (periodic autocorrelations).
    # Objective: minimise E = sum_{k=1}^{n-1} C_k^2, with C_k = sum_i s_i * s_{(i+k) mod n}.
    n = instance["n"]

    m = Model()

    # The sequence values are -1 and +1: an IntVar over {-1, 0, 1} with 0 forbidden.
    seq = m.int_vector("sequence", n, -1, 1)
    for i in range(n):
        m &= (seq[i] != 0)

    # b_i is the literal "s_i = +1".
    b = [(seq[i] >= 1) for i in range(n)]

    # For a pair (i, j), s_i * s_j = +1 when the bits agree and -1 when they differ.
    # So C_k = n - 2 * U_k, where U_k counts the pairs (i, i+k mod n) that differ.
    for k in range(1, n):
        diffs = []
        for i in range(n):
            j = (i + k) % n
            # d is true exactly when b_i and b_j differ (XOR, pinned by four clauses).
            d = m.bool()
            m &= (~d | b[i] | b[j])
            m &= (~d | ~b[i] | ~b[j])
            m &= (d | ~b[i] | b[j])
            m &= (d | b[i] | ~b[j])
            diffs.append(d)

        unequal = m.int(f"unequal_{k}", 0, n)
        m &= (unequal == sum(diffs))

        # Pay (n - 2v)^2 when U_k = v. Exactly one value holds, so the costs add up to C_k^2.
        for v in range(n + 1):
            cost = (n - 2 * v) ** 2
            if cost > 0:
                m.obj[cost] += ~(unequal == v)

    return m, {"sequence": seq}
