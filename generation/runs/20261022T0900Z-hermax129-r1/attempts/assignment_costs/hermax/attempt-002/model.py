from hermax.model import Model


def build(instance):
    cost = instance["cost"]
    num_tasks = len(cost)
    num_people = len(cost[0])

    m = Model()

    # x[i][j] is True if task i is assigned to person j
    x = m.bool_matrix("x", num_tasks, num_people)

    # Each task must be assigned to exactly one person
    for i in range(num_tasks):
        m &= x.row(i).exactly_one()

    # Objective: minimize total cost of assignments
    # Use direct objective form: pay cost[i][j] when x[i][j] is true
    total_cost = sum(cost[i][j] * ~x[i][j] for i in range(num_tasks) for j in range(num_people))
    m.obj += total_cost

    return m, {"x": x}
