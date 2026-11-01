from hermax.model import Model


def build(instance):
    n = 24
    m = Model()

    # Sequence of 24 integers, each in [0, 60]
    x = m.int_vector("x", n, 0, 60)

    # x[0] = 0, x[23] = 14
    m &= (x[0] == 0)
    m &= (x[23] == 14)

    # All elements must be distinct
    m &= x.all_different()

    # For each transition, exactly one of three operations must hold:
    # 1. x[i+1] = x[i] + 5
    # 2. x[i+1] = x[i] + 7
    # 3. x[i+1] = sqrt(x[i]) (only if x[i] is a perfect square)

    for i in range(n - 1):
        # Create auxiliary Boolean variables for each operation
        add5 = m.bool(f"add5_{i}")
        add7 = m.bool(f"add7_{i}")
        sqrt_op = m.bool(f"sqrt_{i}")

        # Exactly one operation is used
        # This is tricky to express in SAT/MaxSAT. We can use:
        # - At least one: add5 | add7 | sqrt_op (already have this)
        # - At most one: (add5 => ~add7), (add5 => ~sqrt_op), (add7 => ~sqrt_op)
        #   Which is equivalent to: ~add5 | ~add7, ~add5 | ~sqrt_op, ~add7 | ~sqrt_op
        m &= (add5 | add7 | sqrt_op)
        m &= (~add5 | ~add7)
        m &= (~add5 | ~sqrt_op)
        m &= (~add7 | ~sqrt_op)

        # Now enforce the operation's consequence:
        # If add5: x[i+1] = x[i] + 5
        m &= (~add5 | (x[i + 1] == x[i] + 5))

        # If add7: x[i+1] = x[i] + 7
        m &= (~add7 | (x[i + 1] == x[i] + 7))

        # If sqrt_op: x[i+1]^2 = x[i]
        # Since we can't express x[i+1]^2 directly, enumerate all pairs
        for sq, root in [(0, 0), (1, 1), (4, 2), (9, 3), (16, 4), (25, 5), (36, 6), (49, 7)]:
            # If sqrt_op and x[i]=sq, then x[i+1]=root
            # ~sqrt_op | x[i]!=sq | x[i+1]=root
            m &= (~sqrt_op | (x[i] != sq) | (x[i + 1] == root))

        # Also: if sqrt_op is true, then x[i] must be a perfect square
        # This should be enforced by the sqrt clauses above
        # If x[i] is not a perfect square, none of the sqrt clauses will allow x[i+1] to be set validly
        # But wait, that's not quite right. The clause ~sqrt_op | x[i]!=sq | x[i+1]=root
        # says: if sqrt_op AND x[i]=sq, then x[i+1]=root
        # But if x[i] doesn't match any sq, then all sqrt clauses are vacuously true
        # So we need an additional constraint

        # If sqrt_op is true, then x[i] must be one of the perfect squares
        for sq in [0, 1, 4, 9, 16, 25, 36, 49]:
            # If sqrt_op, then x[i] must equal one of these values
            # sqrt_op => (x[i] in {0,1,4,9,16,25,36,49})
            # This can be written as: ~sqrt_op | (x[i]=0 | x[i]=1 | ...)
            pass

        # Actually, let's use an auxiliary variable to track if x[i] is perfect
        is_perfect = m.bool(f"is_perfect_{i}")

        # is_perfect is true iff x[i] is a perfect square
        for sq in [0, 1, 4, 9, 16, 25, 36, 49]:
            # If x[i] = sq, then is_perfect should be true
            # x[i] = sq => is_perfect
            m &= ((x[i] != sq) | is_perfect)

        # Also, if is_perfect is true, then x[i] must be one of the perfect squares
        # is_perfect => (x[i] in {0,1,4,9,16,25,36,49})
        sq_values = [0, 1, 4, 9, 16, 25, 36, 49]
        for sq in range(61):
            if sq not in sq_values:
                # If x[i] = sq and sq is not perfect, then is_perfect must be false
                m &= ((x[i] != sq) | ~is_perfect)

        # Finally: if sqrt_op is true, then is_perfect must be true
        m &= (~sqrt_op | is_perfect)

    # Ensure that 2, 10, and 14 appear in that order
    idx_2 = m.int("idx_2", 0, n - 1)
    idx_10 = m.int("idx_10", 0, n - 1)
    idx_14 = m.int("idx_14", 0, n - 1)

    m &= (x[idx_2] == 2)
    m &= (x[idx_10] == 10)
    m &= (x[idx_14] == 14)

    m &= (idx_2 < idx_10)
    m &= (idx_10 < idx_14)

    return m, {"x": x}
