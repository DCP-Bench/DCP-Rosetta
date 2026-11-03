"""Aircraft assignment: assign aircraft of each type to routes to meet passenger demand at minimum cost.

Each type has a limited number of units, each route has a passenger demand, and every
(type, route) pair has a passenger capacity and an operational cost per aircraft.
The decision is how many aircraft of each type fly each route.
"""
import hexaly.optimizer as hx


def build(instance):
    # availability[i]: number of aircraft units of type i; demand[j]: passengers that route j must carry
    availability, demand = instance["availability"], instance["demand"]
    # capabilities[i][j]: passengers one aircraft of type i carries on route j; costs[i][j]: cost of one such aircraft on that route
    capabilities, costs = instance["capabilities"], instance["costs"]
    types, routes = len(availability), len(demand)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # allocation[i][j] is the number of aircraft of type i on route j, at most the units available
    # (the bound availability[i] is what the type has in total, so no value above it can be feasible)
    allocation = [[model.int(0, availability[i]) for _ in range(routes)] for i in range(types)]

    # Stay within the availability limit of each aircraft type: the aircraft of type i
    # sent over all routes do not exceed its available units
    for i in range(types):
        model.constraint(model.sum(allocation[i]) <= availability[i])
    # Meet the passenger demand of every route: the capacity of the aircraft assigned to route j is at least demand[j]
    for j in range(routes):
        model.constraint(model.sum(capabilities[i][j] * allocation[i][j] for i in range(types)) >= demand[j])

    # Minimise the total operational cost of all assigned aircraft
    model.minimize(model.sum(costs[i][j] * allocation[i][j] for i in range(types) for j in range(routes)))
    return optimizer, {"allocation": allocation}
