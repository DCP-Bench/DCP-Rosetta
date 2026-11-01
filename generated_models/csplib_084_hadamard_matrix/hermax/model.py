from hermax.model import Model


def build(instance):
    """Hadamard matrix Legendre pairs problem.

    Find two sequences a[0..l-1] and b[0..l-1] with values in {-1, +1} such that:
    - Periodic autocorrelation function (PAF) constraints: PAF(a,s) + PAF(b,s) = -2
    - Each sequence sums to 1
    """
    l = instance["l"]
    m = (l - 1) // 2

    model = Model()

    # Variables: a and b are arrays with values in {-1, +1}
    # Represent as booleans: a_bool = 1 means a=+1, a_bool = 0 means a=-1
    a_bool = model.bool_vector("a_bool", l)
    b_bool = model.bool_vector("b_bool", l)

    # Constraint: sum(a) = 1
    # sum = sum of (2*bool - 1) = 2*sum(bool) - l = 1
    # => sum(bool) = (l+1)/2
    model &= (sum(a_bool) == (l + 1) // 2)

    # Constraint: sum(b) = 1
    model &= (sum(b_bool) == (l + 1) // 2)

    # Auxiliary products: prod_ij = 1 iff the two booleans have the same value
    # For a[i] = 2*a_bool[i] - 1, a[j] = 2*a_bool[j] - 1
    # a[i] * a[j] = 2*prod_ij - 1, where prod_ij = 1 iff a_bool[i] == a_bool[j]

    a_prod = {}  # a_prod[i][j] = boolean indicating a[i] * a[j] > 0 (same sign)
    b_prod = {}  # b_prod[i][j] = boolean indicating b[i] * b[j] > 0 (same sign)

    for i in range(l):
        for j in range(l):
            # a_prod[i, j] = 1 iff a_bool[i] == a_bool[j]
            # Constraint: a_prod[i,j] => (a_bool[i] & a_bool[j]) | (~a_bool[i] & ~a_bool[j])
            # And reverse: (a_bool[i] & a_bool[j]) | (~a_bool[i] & ~a_bool[j]) => a_prod[i,j]
            # Which is: a_prod[i,j] <=> (a_bool[i] & a_bool[j]) | (~a_bool[i] & ~a_bool[j])

            a_eq = model.bool(f"a_eq_{i}_{j}")
            b_eq = model.bool(f"b_eq_{i}_{j}")

            # a_eq = 1 iff both are true or both are false
            # Implication: a_eq => ((a_bool[i] & a_bool[j]) | (~a_bool[i] & ~a_bool[j]))
            model &= (a_eq | a_bool[i] | a_bool[j])  # ~a_eq | (a_bool[i] | a_bool[j])... this doesn't work

            # Better: use direct encoding
            # a_eq => (a_bool[i] == a_bool[j])
            # means: if a_eq then (a_bool[i] implies a_bool[j]) and (a_bool[j] implies a_bool[i])
            # model &= (~a_eq | (a_bool[i] == a_bool[j]))  # Can't use this

            # Use: a_eq iff (not (a_bool[i] XOR a_bool[j]))
            # XOR: a ^ b = (a | b) & (~a | ~b)
            # XNOR: ~(a ^ b) = (a & b) | (~a & ~b)

            # Constraint: if a_eq is true, then a_bool[i] and a_bool[j] must have same value
            # if a_eq is false, then they must have different values
            model &= (a_eq | a_bool[i] | a_bool[j])    # ~a_eq or a_bool[i] or a_bool[j]
            model &= (a_eq | ~a_bool[i] | ~a_bool[j])  # ~a_eq or ~a_bool[i] or ~a_bool[j]
            model &= (~a_eq | a_bool[i] | ~a_bool[j])  # a_eq or a_bool[i] or ~a_bool[j]
            model &= (~a_eq | ~a_bool[i] | a_bool[j])  # a_eq or ~a_bool[i] or a_bool[j]

            model &= (b_eq | b_bool[i] | b_bool[j])
            model &= (b_eq | ~b_bool[i] | ~b_bool[j])
            model &= (~b_eq | b_bool[i] | ~b_bool[j])
            model &= (~b_eq | ~b_bool[i] | b_bool[j])

            a_prod[(i, j)] = a_eq
            b_prod[(i, j)] = b_eq

    # PAF constraints: PAF(a, s) + PAF(b, s) = -2
    for s in range(1, m + 1):
        # PAF(a, s) = sum(a[i] * a[(i+s) mod l])
        #           = sum(2*a_prod[i, (i+s)%l] - 1)
        #           = 2*sum(a_prod[...]) - l
        paf_a_sum = sum(a_prod[(i, (i + s) % l)] for i in range(l))
        paf_b_sum = sum(b_prod[(i, (i + s) % l)] for i in range(l))

        # paf_a = 2*paf_a_sum - l
        # paf_b = 2*paf_b_sum - l
        # paf_a + paf_b = -2
        # 2*paf_a_sum - l + 2*paf_b_sum - l = -2
        # 2*(paf_a_sum + paf_b_sum) - 2*l = -2
        # paf_a_sum + paf_b_sum = l - 1
        model &= (paf_a_sum + paf_b_sum == l - 1)

    # Convert output back to {-1, +1}
    a_output = [2 * a_bool[i] - 1 for i in range(l)]
    b_output = [2 * b_bool[i] - 1 for i in range(l)]

    return model, {"a": a_output, "b": b_output}
