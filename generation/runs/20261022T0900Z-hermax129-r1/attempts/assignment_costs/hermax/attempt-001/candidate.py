from hermax.model import Model


def build(instance):
    cost = instance["cost"]
    num_tasks = len(cost)
    num_people = len(cost[0])

    m = Model()

    # x[i][j] is True if task i is assigned to person j
    # Each task must be assigned to exactly one person
    x = m.bool_matrix("x", num_tasks, num_people)
    for i in range(num_tasks):
        m &= x.row(i).exactly_one()

    # Objective: minimize total cost of assignments
    # Soft clause polarity: pay when literal is true (when assignment ~x[i][j] happens)
    for i in range(num_tasks):
        for j in range(num_people):
            m.obj[cost[i][j]] += ~x[i][j]

    return m, {"x": x}
