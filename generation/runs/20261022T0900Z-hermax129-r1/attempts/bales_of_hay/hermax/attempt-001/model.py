from hermax.model import Model


def build(instance):
    # Read instance: number of bales and their pairwise sums
    n = instance["n"]
    weights = instance["weights"]

    m = Model()

    # Create integer variables for each bale weight
    # All pairwise sums (n choose 2) are given; infer individual bale weights
    max_weight = max(weights)
    bales = m.int_vector("bales", n, 1, max_weight)

    # Enforce sorted order to break symmetry and reduce search space
    for i in range(n - 1):
        m &= (bales[i] <= bales[i + 1])

    # Generate all pairs: "weighed in all possible combinations of two"
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    num_pairs = len(pairs)
    num_weights = len(weights)

    # Bipartite matching: assign each pair to a weight
    # This models the one-to-one correspondence between pairwise sums and given weights
    match = m.bool_matrix("match", num_pairs, num_weights)

    # Each pair must be matched to exactly one weight (all pairs must appear)
    for p in range(num_pairs):
        m &= match[p].exactly_one()

    # Each weight must be produced by exactly one pair (all given weights are valid)
    for w in range(num_weights):
        m &= match.col(w).exactly_one()

    # Enforce the matching: if pair p is matched to weight w,
    # then bales[i] + bales[j] must equal weights[w]
    for p, (i, j) in enumerate(pairs):
        for w, weight in enumerate(weights):
            s = bales[i] + bales[j]
            # match[p][w] -> (s == weight) encoded as:
            # ~match[p][w] OR (s <= weight AND s >= weight)
            m &= (~match[p, w] | (s <= weight))
            m &= (~match[p, w] | (s >= weight))

    return m, {"bales": bales}
