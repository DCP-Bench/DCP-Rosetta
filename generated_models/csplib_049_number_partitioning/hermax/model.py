from hermax.model import Model


def build(instance):
    N = instance["n"]          # the numbers are 1..N
    h = N // 2                 # A and B have the same cardinality
    S = N * (N + 1) // 2       # sum of 1..N
    Q = N * (N + 1) * (2 * N + 1) // 6   # sum of squares of 1..N

    m = Model()
    # x[i-1] is true when the number i is in A, and false when it is in B.
    x = m.bool_vector("x", N)

    # Same cardinality: A holds half of the numbers.
    m &= (sum(x) == h)
    # Same sum: twice the sum over A equals the total.
    m &= (2 * sum((i + 1) * x[i] for i in range(N)) == S)
    # Same sum of squares: twice the sum of squares over A equals the total.
    m &= (2 * sum((i + 1) * (i + 1) * x[i] for i in range(N)) == Q)

    # Output: the members of A and of B as sorted lists of integers.
    A = m.int_vector("A", h, 1, N)
    B = m.int_vector("B", N - h, 1, N)
    m &= A.increasing()
    m &= B.increasing()

    # Link the lists to x: i is in A exactly when x[i-1] holds.
    for i in range(1, N + 1):
        xi = x[i - 1]
        in_A = [(A[k] == i) for k in range(h)]
        in_B = [(B[k] == i) for k in range(N - h)]

        any_A = in_A[0]
        for lit in in_A[1:]:
            any_A = any_A | lit
        any_B = in_B[0]
        for lit in in_B[1:]:
            any_B = any_B | lit

        # i in A  -> i appears in the A list
        m &= (~xi) | any_A
        # i in B  -> i appears in the B list
        m &= xi | any_B
        # a number listed in A is in A, and a number listed in B is in B
        for lit in in_A:
            m &= (~lit) | xi
        for lit in in_B:
            m &= (~lit) | (~xi)

    return m, {"A": A, "B": B}
