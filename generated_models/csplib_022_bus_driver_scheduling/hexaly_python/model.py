"""Bus driver scheduling: choose shifts that cover every piece of work exactly once, with as few shifts as possible."""
import hexaly.optimizer as hx


def build(instance):
    num_work, shifts = instance["num_work"], instance["shifts"]  # shifts[s]: the pieces of work shift s covers
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[s] = 1 if shift s is selected
    x = [model.bool() for _ in shifts]

    # Every piece of work is covered by exactly one selected shift
    for w in range(num_work):
        model.constraint(model.sum(x[s] for s, covered in enumerate(shifts) if w in covered) == 1)

    # Minimise the number of shifts, all costing the same
    model.minimize(model.sum(x))
    return optimizer, {"x": x}
