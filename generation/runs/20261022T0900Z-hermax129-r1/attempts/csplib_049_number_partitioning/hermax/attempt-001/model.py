from hermax.model import Model


def build(instance):
    n = instance["n"]

    # Constraint: partition numbers 1..n into two sets A and B with:
    # - Equal cardinality (n/2 elements each)
    # - Equal sum
    # - Equal sum of squares

    m = Model()

    size = n // 2

    # Create integer variables for A and B in sorted order
    A = m.int_vector("A", size, 1, n)
    B = m.int_vector("B", size, 1, n)

    # Ensure A and B are sorted
    m &= A.increasing()
    m &= B.increasing()

    # For each number from 1 to n, it must appear in exactly one of A or B
    # Create auxiliary Booleans: in_A[v] = 1 iff v is in A
    in_A = m.bool_vector("in_A", n)

    # For each number v from 1 to n:
    for v in range(1, n + 1):
        # v is in A if it equals some A[i]
        # v is in B if it equals some B[i]
        # Exactly one must be true

        # Create Booleans for "v appears in A/B at position i"
        is_in_A_somewhere = m.bool(f"is_in_A_{v}")
        is_in_B_somewhere = m.bool(f"is_in_B_{v}")

        # is_in_A_somewhere is true iff v equals some element of A
        # (v == A[0]) | (v == A[1]) | ... | (v == A[size-1])
        # But we can't OR Literals directly in constraints
        # We need to express this as a constraint

        # Let's use: is_in_A_somewhere = 1 iff v appears in A
        # This is equivalent to: (A[0] == v) | (A[1] == v) | ... | (A[size-1] == v)

        # In CNF: is_in_A_somewhere = 1 => (some A[i] == v)
        # And: some A[i] == v => is_in_A_somewhere = 1

        # We can write this as:
        # For each position i: (A[i] == v) => is_in_A_somewhere
        # Which is: (~(A[i] == v)) | is_in_A_somewhere

        # And: is_in_A_somewhere => (some A[i] == v)
        # But the "some" is hard to express

        # Alternative: use the channeling constraint
        # in_A[v-1] = 1 iff v is in A
        # Set in_A[v-1] = is_in_A_somewhere

        # For simplicity, let's use: in_A[v-1] is true iff v appears in A
        # We enforce this by checking membership for each position

        # For each position i in A: if A[i] == v, then in_A[v-1] must be 1
        for i in range(size):
            # (A[i] == v) => in_A[v-1]
            # Which is: (~(A[i] == v)) | in_A[v-1]
            m &= (~(A[i] == v)) | in_A[v-1]

        # For each position j in B: if B[j] == v, then in_A[v-1] must be 0
        for j in range(size):
            # (B[j] == v) => ~in_A[v-1]
            # Which is: (~(B[j] == v)) | ~in_A[v-1]
            m &= (~(B[j] == v)) | (~in_A[v-1])

        # Ensure v is in exactly one set
        # At least one of A or B contains v
        # Create: (exists i such that A[i] == v) or (exists j such that B[j] == v)
        # This is: in_A[v-1] | ~in_A[v-1] (always true)
        # So we need to ensure at least one occurrence

        # Actually, the constraints above ensure:
        # - If A contains v, then in_A[v-1] = 1
        # - If B contains v, then in_A[v-1] = 0
        # But they don't force v to be in at least one set

        # Let me add: at least one element in A or B equals v
        # Sum of (A[i] == v) and (B[j] == v) should be >= 1
        # But we can't directly sum Literals

        # Instead, use: in_A[v-1] | ~in_A[v-1] | (some A[i] == v) | (some B[j] == v)
        # The first two are always true, so this is always satisfied

        # I need a different approach
        pass

    # Compute the target sum and sum of squares for each set
    total_sum = n * (n + 1) // 2
    target_sum = total_sum // 2

    total_sum_sq = n * (n + 1) * (2 * n + 1) // 6
    target_sum_sq = total_sum_sq // 2

    # Equal sum: sum of A = target_sum
    m &= (sum(A) == target_sum)

    # For sum of squares, use auxiliary Booleans for each (position, value) pair
    sum_sq_A = 0
    for i in range(size):
        for v in range(1, n + 1):
            is_v = (A[i] == v)
            sum_sq_A += (v * v) * is_v

    sum_sq_B = 0
    for j in range(size):
        for v in range(1, n + 1):
            is_v = (B[j] == v)
            sum_sq_B += (v * v) * is_v

    # Constraint: sum of squares in A = target_sum_sq
    m &= (sum_sq_A == target_sum_sq)

    # Constraint: sum of squares in B = target_sum_sq
    m &= (sum_sq_B == target_sum_sq)

    # Constraint: for each number, it must be in A or B (enforced by sum constraint implicitly)
    # But let's add explicit constraints using in_A
    for v in range(1, n + 1):
        # v must appear somewhere
        # This is ensured by the sum constraints
        # But to be safe, let's add: at least one A[i] == v or B[j] == v

        # Create a sum of all membership Literals
        membership = sum((A[i] == v for i in range(size)), 0)
        membership = membership + sum((B[j] == v for j in range(size)), 0)
        # This sums the Literals (which are 0/1)
        # membership >= 1 means v is in at least one set
        m &= (membership >= 1)

    return m, {"A": A, "B": B}
