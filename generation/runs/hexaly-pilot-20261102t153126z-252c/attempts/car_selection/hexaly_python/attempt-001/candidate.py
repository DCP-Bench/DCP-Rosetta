"""Car selection: assign participants to cars they are interested in, at most one each way, as many as possible."""
import hexaly.optimizer as hx


def build(instance):
    possible = instance["possible_assignments"]  # possible[i][j] = 1 if participant i is interested in car j
    participants, cars = len(possible), len(possible[0]) if possible else 0
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # assignments[i][j] = 1 if participant i gets car j
    assignments = [[model.bool() for _ in range(cars)] for _ in range(participants)]

    for i in range(participants):
        # A participant only gets a car they are interested in
        for j in range(cars):
            if not possible[i][j]:
                model.constraint(assignments[i][j] == 0)
        # Each participant gets at most one car
        model.constraint(model.sum(assignments[i]) <= 1)
    # Each car goes to at most one participant
    for j in range(cars):
        model.constraint(model.sum(assignments[i][j] for i in range(participants)) <= 1)

    # Maximise the number of assignments
    model.maximize(model.sum(assignments[i][j] for i in range(participants) for j in range(cars)))
    return optimizer, {"assignments": assignments}
