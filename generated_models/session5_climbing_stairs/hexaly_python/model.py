"""Climbing stairs: climb n steps in moves of m1 to m2 steps, listing 0 for the moves after reaching the top."""
import hexaly.optimizer as hx


def build(instance):
    # n = number of steps of the stair; m1, m2 = fewest and most steps that one move may take
    n, m1, m2 = instance["n"], instance["m1"], instance["m2"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # steps[i] is the number of steps taken at move i, or 0 when no step is taken. There are n entries because the
    # output lists n moves; the upper bound m2 is the most steps one move may take.
    steps = [model.int(0, m2) for _ in range(n)]

    # Every move is either empty or takes between m1 and m2 steps
    for s in steps:
        model.constraint(model.or_(s == 0, s >= m1))
    # Once a move is empty, all later moves are empty: the stair has been climbed
    for i in range(n - 1):
        model.constraint(steps[i + 1] <= m2 * steps[i])
    # The moves add up to the n steps of the stair
    model.constraint(model.sum(steps) == n)

    return optimizer, {"steps": steps}
