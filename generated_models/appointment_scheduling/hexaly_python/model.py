"""Appointment scheduling: give each person one interview slot they are free in, one person per slot."""
import hexaly.optimizer as hx


def build(instance):
    free = instance["m"]  # free[i][j] = 1 if person i is free in slot j
    people, slots = len(free), len(free[0])
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[i][j] = 1 if person i is interviewed in slot j
    x = [[model.bool() for _ in range(slots)] for _ in range(people)]

    for i in range(people):
        # Every person gets exactly one slot
        model.constraint(model.sum(x[i]) == 1)
        # A person is only scheduled in a slot where they are free
        for j in range(slots):
            if not free[i][j]:
                model.constraint(x[i][j] == 0)
    # Every slot holds exactly one person
    for j in range(slots):
        model.constraint(model.sum(x[i][j] for i in range(people)) == 1)

    return optimizer, {"x": x}
