"""Multi-commodity transportation: ship every product from origins to destinations at minimum cost,
within the total limit on each route."""
import hexaly.optimizer as hx


def build(instance):
    # supply[i][p] = units of product p available at origin i; demand[j][p] = units of product p wanted at
    # destination j; limit[i][j] = most units of all products together that route i -> j can carry;
    # cost[i][j][p] = cost of shipping one unit of product p from origin i to destination j
    supply, demand, limit, cost = instance["supply"], instance["demand"], instance["limit"], instance["cost"]
    # number of origins, destinations and products, read off the shapes of supply and demand
    origins, destinations, products = len(supply), len(demand), len(supply[0])
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # ship[i][j][p] is the amount of product p sent from origin i to destination j; no route
    # carries more than its limit, which bounds each amount
    ship = [[[model.int(0, limit[i][j]) for _ in range(products)] for j in range(destinations)]
            for i in range(origins)]

    for p in range(products):
        # An origin ships out at most its supply of each product (the statement does not say the
        # supply has to be used up)
        for i in range(origins):
            model.constraint(model.sum(ship[i][j][p] for j in range(destinations)) <= supply[i][p])
        # Each destination receives exactly its demand of each product
        for j in range(destinations):
            model.constraint(model.sum(ship[i][j][p] for i in range(origins)) == demand[j][p])
    # The products on a route together stay within its limit
    for i in range(origins):
        for j in range(destinations):
            model.constraint(model.sum(ship[i][j]) <= limit[i][j])

    # Minimise the total shipping cost
    total_cost = model.sum(cost[i][j][p] * ship[i][j][p]
                           for i in range(origins) for j in range(destinations) for p in range(products))
    model.minimize(total_cost)
    return optimizer, {"total_cost": total_cost}
