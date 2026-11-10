"""Clock triplets: arrange 1..12 round a clock face so that no three adjacent numbers add up to more than 21."""
import hexaly.optimizer as hx


def build(instance):
    n = 12
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # The numbers 1..12, each once, in clock order: a full list decision
    perm = model.list(n)
    model.constraint(model.count(perm) == n)
    x = [perm[i] + 1 for i in range(n)]

    # Every three adjacent numbers (the clock wraps round) add up to at most 21
    for i in range(n):
        model.constraint(x[i] + x[(i + 1) % n] + x[(i + 2) % n] <= 21)

    return optimizer, {"x": x}
