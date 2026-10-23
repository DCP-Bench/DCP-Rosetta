from hermax.model import Model


def build(instance):
    names = instance["warehouse_s"]
    fixed = instance["fixed_costs"]
    cap = instance["max_shipping"]
    demands = instance["demands"]
    cost = instance["shipping_costs"]

    W = len(fixed)     # warehouses
    R = len(demands)   # regions

    # Warehouse positions by city name (the names are fixed by the problem).
    ny = names.index("New York")
    la = names.index("Los Angeles")
    atl = names.index("Atlanta")

    m = Model()
    open_w = m.bool_vector("open", W)
    # A region never takes more than its demand, nor a warehouse more than its capacity.
    ships = [[m.int(f"ships_{i}_{j}", 0, min(cap, demands[j])) for j in range(R)] for i in range(W)]

    # Every region's demand is met exactly.
    for j in range(R):
        m &= (sum(ships[i][j] for i in range(W)) == demands[j])

    # A warehouse ships at most its capacity; a closed warehouse ships nothing.
    # Unit-coefficient sums keep the capacity out of a weighted Boolean term.
    for i in range(W):
        m &= (sum(ships[i][j] for j in range(R)) <= cap)
        for j in range(R):
            m &= (ships[i][j] == 0).only_if(~open_w[i])

    # Restriction 1: New York open implies Los Angeles open.
    m &= (~open_w[ny] | open_w[la])
    # Restriction 2: at most three warehouses operational.
    m &= (sum(open_w[i] for i in range(W)) <= 3)
    # Restriction 3: Atlanta or Los Angeles open.
    m &= (open_w[atl] | open_w[la])

    # Total cost: fixed costs of open warehouses plus shipping costs.
    total = sum(fixed[i] * open_w[i] for i in range(W)) + sum(
        cost[i][j] * ships[i][j] for i in range(W) for j in range(R)
    )
    m.obj += total

    return m, {"open_warehouse": open_w, "ships": ships, "total_cost": total}
