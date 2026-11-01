from hermax.model import Model


def build(instance):
    n = instance["n"]
    weights = instance["weights"]

    m = Model()

    # Create integer variables for each bale weight
    max_weight = max(weights)
    bales = m.int_vector("bales", n, 1, max_weight)

    # Symmetry breaking: enforce sorted order
    for i in range(n - 1):
        m &= (bales[i] <= bales[i + 1])

    # Create list of all pairs (i, j) where i < j
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    num_pairs = len(pairs)
    num_weights = len(weights)

    # Bipartite matching: assign each pair to a weight
    # match[p][w] = true means pair p produces weight at index w
    match = m.bool_matrix("match", num_pairs, num_weights)

    # Each pair is matched to exactly one weight
    for p in range(num_pairs):
        m &= match[p].exactly_one()

    # Each weight is used by exactly one pair
    for w in range(num_weights):
        m &= match.col(w).exactly_one()

    # For each assignment: if match[p][w] is true,
    # then bales[i] + bales[j] = weights[w]
    for p, (i, j) in enumerate(pairs):
        for w, weight in enumerate(weights):
            # When match[p][w] is selected, the sum must equal weight
            # Use indicator constraints: match[p][w] implies bales[i]+bales[j] == weight
            # Contrapositive: if bales[i]+bales[j] != weight, then match[p][w] = false
            # Split inequality into two directions for the MaxSAT solver

            # Create a sum variable
            s = bales[i] + bales[j]

            # match[p][w] -> (s == weight)
            # Equivalent to: ~match[p][w] OR (s == weight)
            # We cannot directly post (s == weight) in a disjunction
            # So we decompose: ~match[p][w] OR ((s <= weight) AND (s >= weight))
            # Which gives us: (~match[p][w] OR s <= weight) AND (~match[p][w] OR s >= weight)
            m &= (~match[p, w] | (s <= weight))
            m &= (~match[p, w] | (s >= weight))

    return m, {"bales": bales}
