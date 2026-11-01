from hermax.model import Model


def build(instance):
    n = instance["n"]

    # Number of triples required: n*(n-1)/6
    num_triples = n * (n - 1) // 6

    m = Model()

    # Create boolean matrix: sets[i][j] = True if element j is in triple i
    # (elements are represented as 0 to n-1 for values 1 to n)
    sets = m.bool_matrix("sets", num_triples, n)

    # Constraint 1: Each triple has exactly 3 elements (each row has exactly 3 ones)
    for i in range(num_triples):
        m &= (sum(sets[i][k] for k in range(n)) == 3)

    # Constraint 2: Any two triples have at most one common element
    # For any two rows i and j, at most one element can appear in both
    for i in range(num_triples):
        for j in range(i + 1, num_triples):
            # Create auxiliary booleans for each element
            # common_ijk is True iff both sets[i][k] and sets[j][k] are True
            common_bools = []
            for k in range(n):
                common_k = m.bool(f"common_{i}_{j}_{k}")
                # Reify: common_k is True iff sets[i][k] AND sets[j][k]
                # Implement: common_k <= sets[i][k], common_k <= sets[j][k]
                #            common_k >= sets[i][k] + sets[j][k] - 1
                m &= (common_k <= sets[i][k])
                m &= (common_k <= sets[j][k])
                m &= (common_k >= sets[i][k] + sets[j][k] - 1)
                common_bools.append(common_k)

            # At most 1 common element
            m &= (sum(common_bools) <= 1)

    return m, {"sets": sets}
