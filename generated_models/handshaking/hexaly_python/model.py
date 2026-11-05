"""Handshaking: Hilary, Jocelyn and their guest couples shake hands; everybody Jocelyn asks gives a different
count. How many hands did Hilary shake?"""
from itertools import combinations

import hexaly.optimizer as hx


def build(instance):
    couples = instance["num_couples"] + 1  # the guests and the hosts
    people = 2 * couples  # person 2c and person 2c + 1 are married; Hilary is 0, Jocelyn 1
    hilary, jocelyn = 0, 1
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # shake[a, b] = 1 if a and b shake hands; nobody shakes with him- or herself or the spouse
    shake = {(a, b): model.bool() for a, b in combinations(range(people), 2) if a // 2 != b // 2}
    shaken = [model.sum(v for (a, b), v in shake.items() if p in (a, b)) for p in range(people)]

    # has[p][c] = 1 if person p has shaken c hands. Booleans with linear sums let Hexaly treat the counts and
    # the "all different" rule as one linear system, which it can also prove things about.
    has = [[model.bool() for _ in range(people)] for _ in range(people)]
    for p in range(people):
        model.constraint(model.sum(has[p]) == 1)
        model.constraint(model.sum(c * has[p][c] for c in range(people)) == shaken[p])

    # Everybody Jocelyn asks, Hilary included, gives a different answer
    asked = [p for p in range(people) if p != jocelyn]
    for c in range(people):
        model.constraint(model.sum(has[p][c] for p in asked) <= 1)

    return optimizer, {"hil": shaken[hilary]}
