"""Initials queue: ten people with different alphabetically ordered pairs of the letters A..E as initials, none
sharing a letter with the person in front, BE first, CD second and BD last."""
from itertools import combinations

import hexaly.optimizer as hx

LETTERS = "ABCDE"
PAIRS = list(combinations(range(5), 2))  # the ten possible initials, as letter numbers 0..4


def build(instance):
    n = len(PAIRS)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # order[i] is the pair (an index into PAIRS) of the person in position i; every pair is used once,
    # so no two people have the same initials
    order = model.list(n)
    model.constraint(model.count(order) == n)
    first = model.array([a for a, _ in PAIRS])
    second = model.array([b for _, b in PAIRS])
    queue = [[model.at(first, order[i]), model.at(second, order[i])] for i in range(n)]

    # Nobody shares a letter with the person in front of them
    for i in range(n - 1):
        for p in queue[i]:
            for q in queue[i + 1]:
                model.constraint(p != q)
    # BE is at the front, CD right behind, and BD at the end
    pair = lambda letters: PAIRS.index((LETTERS.index(letters[0]), LETTERS.index(letters[1])))
    model.constraint(order[0] == pair("BE"))
    model.constraint(order[1] == pair("CD"))
    model.constraint(order[n - 1] == pair("BD"))

    return optimizer, {"queue": queue}
