"""Frog circle: arrange cards 1..n in a circle so that a frog starting on card 1 and jumping k places from
card k lands on every card."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[i] is the card at position i of the circle: a permutation, listed from card 1 (the
    # circle has no first position, so starting the list at card 1 picks one rotation)
    perm = model.list(n)
    model.constraint(model.count(perm) == n)
    x = [perm[i] + 1 for i in range(n)]
    model.constraint(x[0] == 1)

    # The frog's position after each jump: from position q it moves x[q] places clockwise
    cards = model.array(x)
    pos = [0]
    for _ in range(n - 1):
        pos.append((pos[-1] + model.at(cards, pos[-1])) % n)
    # It lands on every card: its n positions are all different
    for a in range(n):
        for b in range(a + 1, n):
            model.constraint(pos[a] != pos[b])

    return optimizer, {"x": x}
