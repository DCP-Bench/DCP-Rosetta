from hermax.model import Model


def build(instance):
    """
    Car selection problem: maximize the number of participant-to-car assignments.
    Each participant may be interested in a subset of cars. Each participant is
    assigned to at most one car, and each car is assigned to at most one participant.

    Instance: possible_assignments[i][j] = 1 if participant i can be assigned to car j
    Output: assignments[i][j] = 1 if participant i is assigned to car j
    """
    possible = instance["possible_assignments"]
    n_participants = len(possible)
    n_cars = len(possible[0]) if possible else 0

    m = Model()

    # assignments[i][j] = 1 if participant i is assigned to car j
    assignments = m.bool_matrix("assignments", n_participants, n_cars)

    # Each participant assigned to at most one car
    for i in range(n_participants):
        m &= assignments.row(i).at_most_one()

    # Each car assigned to at most one participant
    for j in range(n_cars):
        m &= assignments.col(j).at_most_one()

    # Only assign if possible
    for i in range(n_participants):
        for j in range(n_cars):
            if not possible[i][j]:
                m &= ~assignments[i][j]

    # Maximize total assignments
    # Pay when assignments[i][j] is FALSE (i.e., when NOT assigned)
    for i in range(n_participants):
        for j in range(n_cars):
            if possible[i][j]:
                m.obj[1] += assignments[i][j]

    return m, {"assignments": assignments}
