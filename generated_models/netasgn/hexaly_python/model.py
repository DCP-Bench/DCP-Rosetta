"""Project assignment: assign hours from people to projects, within each pair's limit, at minimum cost."""
import hexaly.optimizer as hx


def build(instance):
    # supply[i] = hours person i has available; demand[j] = hours project j requires
    # cost[i][j] = cost per hour of person i working on project j; limit[i][j] = most hours person i can give project j
    supply, demand, cost, limit = instance["supply"], instance["demand"], instance["cost"], instance["limit"]
    people, projects = len(supply), len(demand)  # number of people, number of projects
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

    # Minimise the total cost: hours assigned times the cost per hour of that person on that project
    total_cost = model.sum(cost[i][j] * assign[i][j] for i in range(people) for j in range(projects))
    model.minimize(total_cost)
    return optimizer, {"assign": assign, "total_cost": total_cost}
