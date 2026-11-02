"""Aircraft assignment: assign aircraft of each type to routes to meet passenger demand at minimum cost."""
import hexaly.optimizer as hx


def build(instance):
    availability, demand = instance["availability"], instance["demand"]
    capabilities, costs = instance["capabilities"], instance["costs"]
    types, routes = len(availability), len(demand)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # allocation[i][j] is the number of aircraft of type i on route j, at most the units available
    allocation = [[model.int(0, availability[i]) for _ in range(routes)] for i in range(types)]

    # No type is used beyond its available units
    for i in range(types):
        model.constraint(model.sum(allocation[i]) <= availability[i])
    # The passenger capacity on each route meets its demand
    for j in range(routes):
        model.constraint(model.sum(capabilities[i][j] * allocation[i][j] for i in range(types)) >= demand[j])

    # Minimise the total operational cost
    model.minimize(model.sum(costs[i][j] * allocation[i][j] for i in range(types) for j in range(routes)))
    return optimizer, {"allocation": allocation}
