from hermax.model import Model


def build(instance):
    names = instance["warehouse_s"]
    fixed = instance["fixed_costs"]
    cost = instance["shipping_costs"]
    demands = instance["demands"]
    cap = instance["max_shipping"]
    n_w = len(names)
    n_r = len(demands)

    ny = names.index("New York")
    la = names.index("Los Angeles")
    atl = names.index("Atlanta")

    m = Model()
    open_w = m.bool_vector("open", n_w)

    # Each shipment is written over binary digits, so every constraint and the
    # objective below are linear in Booleans.
    ships = []
    for i in range(n_w):
        row = []
        for j in range(n_r):
            ub = min(cap, demands[j])
            b = m.bool_vector(f"sb_{i}_{j}", ub.bit_length())
            row.append(sum(2 ** k * b[k] for k in range(len(b))))
        ships.append(row)

    # Restriction 1: if New York is opened, Los Angeles must also be opened.
    m &= (open_w[la] | ~open_w[ny])

    # Restriction 2: no more than three warehouses can be operational.
    m &= (sum(open_w[i] for i in range(n_w)) <= 3)

    # Restriction 3: either Atlanta or Los Angeles must be opened.
    m &= (open_w[atl] | open_w[la])

    # Every region's demand is met exactly by the shipments.
    for j in range(n_r):
        m &= (sum(ships[i][j] for i in range(n_w)) >= demands[j])

    # A warehouse ships at most its capacity, and nothing if it is closed.
    for i in range(n_w):
        m &= (sum(ships[i][j] for j in range(n_r)) <= cap * open_w[i])

    # Minimise fixed opening costs plus shipping costs.
    total = sum(fixed[i] * open_w[i] for i in range(n_w)) + sum(
        cost[i][j] * ships[i][j] for i in range(n_w) for j in range(n_r)
    )
    m.obj += total

    outputs = {"open_warehouse": open_w, "ships": ships, "total_cost": total}
    return m, outputs
