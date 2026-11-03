"""Finding celebrities: a celebrity is known by everybody else and knows only other celebrities; there is at least one.

Given who knows whom at a party, decide for each person whether they are a celebrity.
"""
import hexaly.optimizer as hx


def build(instance):
    # graph[i][j] = 1 if person i knows person j: row i lists the people person i knows (one row and column per person)
    knows = instance["graph"]
    n = len(knows)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # celebrities[c] = 1 if person c is a celebrity
    celebrities = [model.bool() for _ in range(n)]

    for c in range(n):
        # Everybody else knows c (read from the data, so this is a plain Python truth value)
        known_by_all = all(knows[i][c] for i in range(n) if i != c)
        # c knows only celebrities: every other person c knows is a celebrity (true if c knows nobody)
        only_celebrities = model.and_(*[celebrities[j] for j in range(n) if j != c and knows[c][j]]) \
            if any(knows[c][j] for j in range(n) if j != c) else 1
        # c is a celebrity exactly when both hold
        model.constraint(celebrities[c] == (only_celebrities if known_by_all else 0))

    # At least one celebrity is present at the party
    model.constraint(model.sum(celebrities) >= 1)
    return optimizer, {"celebrities": celebrities}
