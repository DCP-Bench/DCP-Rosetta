"""Water bucket: pour water between buckets until the goal state is reached with the fewest transfers."""
from itertools import product

import hexaly.optimizer as hx


def build(instance):
    cap, initial, goal = instance["capacities"], instance["initial_state"], instance["goal_state"]  # buckets, start, goal
    steps, pad = instance["MAX_STEPS"], instance["PADDING_VALUE"]  # states in the sequence, and the padding value
    n = len(cap)

    # The states the buckets can be in: every way to hold the water there is. A transfer pours from bucket f into
    # bucket g until f is empty or g is full.
    states = [s for s in product(*(range(c + 1) for c in cap)) if sum(s) == sum(initial)]
    index = {s: i for i, s in enumerate(states)}
    successors = []
    for s in states:
        following = set()
        for f in range(n):
            for g in range(n):
                moved = min(s[f], cap[g] - s[g]) if f != g else 0
                if moved > 0:
                    t = list(s)
                    t[f] -= moved
                    t[g] += moved
                    following.add(index[tuple(t)])
        successors.append(sorted(following))
    start, end = index[tuple(initial)], index[tuple(goal)]

    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # at[t][s] = 1 if the sequence is in state s at step t; padded[t] = 1 once the sequence has ended. Booleans
    # over the few states a transfer can reach give Hexaly bounds that moving water amounts around do not.
    at = [[model.bool() for _ in states] for _ in range(steps)]
    padded = [model.bool() for _ in range(steps)]

    # Every step is in one state, or padding after the goal
    for t in range(steps):
        model.constraint(model.sum(at[t]) + padded[t] == 1)
    # The sequence starts in the initial state
    model.constraint(at[0][start] == 1)
    for t in range(steps - 1):
        # The sequence stops at the first goal state, and padding follows it to the end
        model.constraint(padded[t + 1] >= at[t][end])
        model.constraint(padded[t + 1] <= padded[t] + at[t][end])
        # Any other state is followed by a state one transfer away
        for s in range(len(states)):
            if s != end:
                model.constraint(at[t][s] <= model.sum([at[t + 1][u] for u in successors[s]]))
    # The goal has been reached by the last step
    for s in range(len(states)):
        if s != end:
            model.constraint(at[steps - 1][s] == 0)

    # Minimise the number of transfers: one for every state of the sequence after the first
    cost = steps - model.sum(padded) - 1
    model.minimize(cost)

    # The water in each bucket at every step, padded with the padding value after the goal
    sequence = [[model.sum(states[s][b] * at[t][s] for s in range(len(states))) + pad * padded[t]
                 for b in range(n)] for t in range(steps)]
    return optimizer, {"cost": cost, "sequence": sequence}
