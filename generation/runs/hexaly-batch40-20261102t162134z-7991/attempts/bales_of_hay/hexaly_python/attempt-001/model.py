"""Bales of hay: find the weights of n bales from the sorted list of the weights of every pair of bales."""
from itertools import combinations

import hexaly.optimizer as hx


def build(instance):
    n, weights = instance["n"], instance["weights"]
    pairs = list(combinations(range(n), 2))
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # bales[i] is the weight of bale i; no bale weighs more than the heaviest pair
    bales = [model.int(0, max(weights)) for _ in range(n)]
    # Listed in ascending order: the pair weights cannot tell the bales apart, so this picks
    # one of the orderings and is a solution under any reading
    for i in range(n - 1):
        model.constraint(bales[i] <= bales[i + 1])

    # match[q][k] = 1 if pair q is the pair whose combined weight is weights[k]
    match = [[model.bool() for _ in weights] for _ in pairs]
    # Every pair is one written-down weight, and every written-down weight is one pair
    for q in range(len(pairs)):
        model.constraint(model.sum(match[q]) == 1)
    for k in range(len(weights)):
        model.constraint(model.sum(match[q][k] for q in range(len(pairs))) == 1)
    # A pair weighs the weight it is matched with
    for q, (i, j) in enumerate(pairs):
        model.constraint(bales[i] + bales[j] == model.sum(w * match[q][k] for k, w in enumerate(weights)))

    return optimizer, {"bales": bales}
