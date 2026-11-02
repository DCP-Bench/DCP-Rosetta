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

    # Everybody Jocelyn asks, Hilary included, gives a different answer
    asked = [p for p in range(people) if p != jocelyn]
    for a, b in combinations(asked, 2):
        model.constraint(shaken[a] != shaken[b])

    return optimizer, {"hil": shaken[hilary]}
