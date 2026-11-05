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

    # at[i][p] = 1 if the person in position i has the initials PAIRS[p]
    at = [[model.bool() for _ in range(n)] for _ in range(n)]
    # Everyone has one pair of initials, and no two people have the same
    for i in range(n):
        model.constraint(model.sum(at[i]) == 1)
    for p in range(n):
        model.constraint(model.sum(at[i][p] for i in range(n)) == 1)

    # Nobody shares a letter with the person in front: pairs with a common letter cannot stand next to
    # each other
    for i in range(n - 1):
        for p, first in enumerate(PAIRS):
            for q, second in enumerate(PAIRS):
                if p != q and set(first) & set(second):
                    model.constraint(at[i][p] + at[i + 1][q] <= 1)

    # BE is at the front, CD right behind, and BD at the end
    pair = lambda letters: PAIRS.index((LETTERS.index(letters[0]), LETTERS.index(letters[1])))
    model.constraint(at[0][pair("BE")] == 1)
    model.constraint(at[1][pair("CD")] == 1)
    model.constraint(at[n - 1][pair("BD")] == 1)

    # The initials of each person, as two letter numbers 0..4
    queue = [[model.sum(PAIRS[p][k] * at[i][p] for p in range(n)) for k in range(2)] for i in range(n)]
    return optimizer, {"queue": queue}
