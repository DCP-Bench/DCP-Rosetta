from hermax.model import Model


def build(instance):
    n_stores = instance["n_stores"]
    n_wh = instance["n_suppliers"]
    capacity = instance["capacity"]
    cost = instance["cost_matrix"]          # cost[store][warehouse]
    building = instance["building_cost"]

    m = Model()
    y = m.bool_vector("open", n_wh)                     # warehouse j is open
    x = m.bool_matrix("x", n_stores, n_wh)              # store i supplied by warehouse j
    assign = m.int_vector("assign", n_stores, 0, n_wh - 1)

    # Each store is supplied by exactly one warehouse.
    for i in range(n_stores):
        m &= x.row(i).exactly_one()

    # A store can only be supplied by an open warehouse.
    for i in range(n_stores):
        for j in range(n_wh):
            m &= (~x[i][j]) | y[j]

    # Warehouse capacity limits the number of stores it can supply.
    for j in range(n_wh):
        m &= (sum(x[i][j] for i in range(n_stores)) <= capacity[j])

    # Output: the warehouse index chosen for each store.
    for i in range(n_stores):
        for j in range(n_wh):
            m &= x[i][j].implies(assign[i] == j)

    # Total cost: maintenance of open warehouses plus supply costs of stores.
    total = sum(building * y[j] for j in range(n_wh)) + \
        sum(cost[i][j] * x[i][j] for i in range(n_stores) for j in range(n_wh))
    m.obj += total

    return m, {"open_warehouses": y, "supplier_assignment": assign, "total_cost": total}
