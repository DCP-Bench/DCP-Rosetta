"""Finding celebrities: a celebrity is known by everybody else and knows only other celebrities; there is at least one."""
import hexaly.optimizer as hx


def build(instance):
    knows = instance["graph"]  # knows[i][j] = 1 if person i knows person j
    n = len(knows)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    celebrities = [model.bool() for _ in range(n)]

    for c in range(n):
        # Everybody else knows c (read from the data)
        known_by_all = all(knows[i][c] for i in range(n) if i != c)
        # c knows only celebrities
        only_celebrities = model.and_(*[celebrities[j] for j in range(n) if j != c and knows[c][j]]) \
            if any(knows[c][j] for j in range(n) if j != c) else 1
        # c is a celebrity exactly when both hold
        model.constraint(celebrities[c] == (only_celebrities if known_by_all else 0))

    # At least one celebrity is present
    model.constraint(model.sum(celebrities) >= 1)
    return optimizer, {"celebrities": celebrities}
