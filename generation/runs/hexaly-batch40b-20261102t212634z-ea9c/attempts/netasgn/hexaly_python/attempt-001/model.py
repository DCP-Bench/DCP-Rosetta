"""Project assignment: assign hours from people to projects, within each pair's limit, at minimum cost."""
import hexaly.optimizer as hx


def build(instance):
    supply, demand, cost, limit = instance["supply"], instance["demand"], instance["cost"], instance["limit"]
    people, projects = len(supply), len(demand)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # assign[i][j] is the hours person i works on project j, at most their limit for it
    assign = [[model.int(0, limit[i][j]) for j in range(projects)] for i in range(people)]

    # Every person works exactly their available hours
    for i in range(people):
        model.constraint(model.sum(assign[i]) == supply[i])
    # Every project gets exactly the hours it requires
    for j in range(projects):
        model.constraint(model.sum(assign[i][j] for i in range(people)) == demand[j])

    # Minimise the total cost
    total_cost = model.sum(cost[i][j] * assign[i][j] for i in range(people) for j in range(projects))
    model.minimize(total_cost)
    return optimizer, {"assign": assign, "total_cost": total_cost}
