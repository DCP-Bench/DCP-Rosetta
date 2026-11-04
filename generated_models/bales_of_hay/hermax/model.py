# bales_of_hay: a hermax (Python) model from DCP Rosetta.
# Download the `bales_of_hay.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
# Then run it on the first instance (after `pip install hermax`):
#   python bales_of_hay.py bales_of_hay.json

from hermax.model import Model


def create_model(instance):
    """Recover the weight of each of n hay bales. The bales were weighed in every
    combination of two, and the n(n-1)/2 pair weights were written down in numerical
    order without saying which pair gave which weight. Find bale weights that make
    the pair weights, as a list, exactly those written down."""
    n = instance["n"]              # n: the number of bales
    weights = instance["weights"]  # weights: the pair weights, one per pair of bales, in numerical order

    m = Model()

    # bales[i] is the weight of bale i (a weight is never negative, and no bale outweighs the heaviest pair)
    bales = m.int_vector("bales", n, 0, max(weights))

    # The pairs of bales, in a fixed order: (0, 1), (0, 2), ..., (n-2, n-1).
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]

    # pair_weight[p] is the combined weight of the p-th pair of bales.
    # It is one of the written-down weights, so it lies between the smallest and the largest.
    pair_weight = m.int_vector("pair_weight", len(pairs), min(weights), max(weights))
    for p, (i, j) in enumerate(pairs):
        # The weight of a pair is the sum of the weights of its two bales.
        m &= (pair_weight[p] == bales[i] + bales[j])

    # The pair weights are exactly the written-down list: each value occurs among the pairs
    # as many times as it occurs in the list (the values need not be distinct).
    for value in sorted(set(weights)):
        m &= (sum(pair_weight[p] == value for p in range(len(pairs))) == weights.count(value))

    return m, {"bales": bales}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
