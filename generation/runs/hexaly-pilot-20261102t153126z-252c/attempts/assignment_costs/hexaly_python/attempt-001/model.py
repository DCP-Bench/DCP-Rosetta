"""Assignment: give every task to exactly one person, each person at most one task, at minimum total cost."""
import hexaly.optimizer as hx


def build(instance):
    cost = instance["cost"]  # cost[i][j]: cost of task i done by person j
    tasks, people = len(cost), len(cost[0])
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[i][j] = 1 if task i is assigned to person j
    x = [[model.bool() for _ in range(people)] for _ in range(tasks)]

    # Each task is assigned to exactly one person
    for i in range(tasks):
        model.constraint(model.sum(x[i]) == 1)
    # A person takes at most one task; not every person needs one
    for j in range(people):
        model.constraint(model.sum(x[i][j] for i in range(tasks)) <= 1)

    # Minimise the total cost of the assignment
    model.minimize(model.sum(cost[i][j] * x[i][j] for i in range(tasks) for j in range(people)))

    return optimizer, {"x": x}
