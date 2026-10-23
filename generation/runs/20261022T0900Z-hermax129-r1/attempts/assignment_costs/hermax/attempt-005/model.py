from hermax.model import Model


def build(instance):
    cost = instance["cost"]
    n_tasks = len(cost)          # tasks: rows of the cost matrix
    n_people = len(cost[0])      # people: columns of the cost matrix

    m = Model()
    x = m.bool_matrix("x", n_tasks, n_people)

    # Each task goes to exactly one person.
    for i in range(n_tasks):
        m &= x.row(i).exactly_one()

    # Each person takes at most one task ("may take only one of them").
    for j in range(n_people):
        m &= x.col(j).at_most_one()

    # Minimise the total cost of the assignment (linear objective).
    m.obj += sum(cost[i][j] * x[i][j] for i in range(n_tasks) for j in range(n_people))

    return m, {"x": x}
