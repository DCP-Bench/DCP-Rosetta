"""Frog circle: arrange cards 1..n in a circle so that a frog starting on card 1 and jumping k places from
card k lands on every card."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # card[p][k] = 1 if position p of the circle holds card k + 1. Booleans with linear sums let Hexaly treat
    # the arrangement and the frog's path as one linear system, which it can also prove things about.
    card = [[model.bool() for _ in range(n)] for _ in range(n)]
    for p in range(n):
        model.constraint(model.sum(card[p]) == 1)   # one card per position
    for k in range(n):
        model.constraint(model.sum(card[p][k] for p in range(n)) == 1)   # each card once
    # The circle has no first position, so the list starts at card 1
    model.constraint(card[0][0] == 1)

    # at[t][p] = 1 if the frog is at position p after t jumps; it lands on n different positions, so on every card
    at = [[model.bool() for _ in range(n)] for _ in range(n)]
    for t in range(n):
        model.constraint(model.sum(at[t]) == 1)   # one position per jump
    for p in range(n):
        model.constraint(model.sum(at[t][p] for t in range(n)) == 1)   # every position once
    model.constraint(at[0][0] == 1)   # it starts on card 1

    # From position p holding card k + 1 the frog moves k + 1 places clockwise
    for t in range(n - 1):
        for p in range(n):
            for k in range(n):
                model.constraint(at[t][p] + card[p][k] - 1 <= at[t + 1][(p + k + 1) % n])

    x = [model.sum((k + 1) * card[p][k] for k in range(n)) for p in range(n)]
    return optimizer, {"x": x}
