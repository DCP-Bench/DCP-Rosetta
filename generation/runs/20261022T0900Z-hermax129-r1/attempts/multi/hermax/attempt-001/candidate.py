from hermax.model import Model


def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    limit = instance["limit"]
    cost = instance["cost"]

    n_orig = len(supply)
    n_dest = len(demand)
    n_prod = len(supply[0])

    m = Model()
    # ship[i][j][p] is the number of units of product p sent from origin i
    # to destination j. It cannot exceed what either end can handle.
    ship = [
        [
            [
                m.int(f"x_{i}_{j}_{p}", 0, min(supply[i][p], demand[j][p]))
                for p in range(n_prod)
            ]
            for j in range(n_dest)
        ]
        for i in range(n_orig)
    ]

    # An origin ships at most its supply of each product.
    for i in range(n_orig):
        for p in range(n_prod):
            m &= (sum(ship[i][j][p] for j in range(n_dest)) <= supply[i][p])

    # Each destination receives exactly its demand of each product.
    for j in range(n_dest):
        for p in range(n_prod):
            m &= (sum(ship[i][j][p] for i in range(n_orig)) == demand[j][p])

    # The total of all products on a lane stays within the lane limit.
    for i in range(n_orig):
        for j in range(n_dest):
            m &= (sum(ship[i][j][p] for p in range(n_prod)) <= limit[i][j])

    # Minimise the shipping cost over all lanes and products.
    total = sum(
        cost[i][j][p] * ship[i][j][p]
        for i in range(n_orig)
        for j in range(n_dest)
        for p in range(n_prod)
    )
    m.obj += total
    return m, {"total_cost": total}
