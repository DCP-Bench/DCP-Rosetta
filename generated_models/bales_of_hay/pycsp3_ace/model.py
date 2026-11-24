# bales_of_hay: a PyCSP3 model from DCP Rosetta.
# Download the `bales_of_hay.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python bales_of_hay.py bales_of_hay.json

from pycsp3 import *


def create_model(instance):
    """There are n bales of hay. They were weighed in every combination of two, and the pair
    weights were written down in numerical order without saying which pair gave which weight.
    Find the weight of each bale."""
    n_bales = instance["n"]          # the number of bales
    weights = instance["weights"]    # the weight of every pair of bales, in numerical order

    n_pairs = len(weights)           # one weight per pair of bales
    distinct_weights = sorted(set(weights))  # the weights that occur in the list, each once
    # A weight is not negative, so each bale weighs no more than the heaviest pair,
    # which holds that bale and another one.
    heaviest_pair = weights[-1]

    # bales[i] is the weight of bale i.
    bales = VarArray(size=n_bales, dom=range(heaviest_pair + 1))
    # pair_weights[k] is the combined weight of the k-th pair of bales. Its values are
    # among the weights given, so its domain is closed to them.
    pair_weights = VarArray(size=n_pairs, dom=distinct_weights)

    # The pairs of bales, each pair once: (i, j) with i < j.
    pairs = [(i, j) for i in range(n_bales) for j in range(i + 1, n_bales)]

    satisfy(
        # Each pair weighs the sum of its two bales.
        [pair_weights[k] == bales[i] + bales[j] for k, (i, j) in enumerate(pairs)],
        # The pair weights are the given weights: each weight occurs among them as often as it
        # occurs in the list.
        Cardinality(pair_weights, occurrences={w: weights.count(w) for w in distinct_weights}),
    )

    return {"bales": bales}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
