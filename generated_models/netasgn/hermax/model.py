from hermax.model import Model


def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    cost = instance["cost"]
    limit = instance["limit"]
    n_people = len(supply)
    n_projects = len(demand)

    m = Model()
    # assign[i][j] is the number of hours person i works on project j,
    # bounded by the per-pair limit from the instance.
    assign = [
        [m.int(f"assign_{i}_{j}", 0, limit[i][j]) for j in range(n_projects)]
        for i in range(n_people)
    ]

    # Each person's assigned hours add up to their supply.
    for i in range(n_people):
        m &= (sum(assign[i][j] for j in range(n_projects)) == supply[i])

    # Each project's assigned hours add up to its demand.
    for j in range(n_projects):
        m &= (sum(assign[i][j] for i in range(n_people)) == demand[j])

    # Minimise the total cost of the hours assigned.
    total_cost = sum(cost[i][j] * assign[i][j]
                     for i in range(n_people) for j in range(n_projects))
    m.obj += total_cost

    return m, {"assign": assign, "total_cost": total_cost}
