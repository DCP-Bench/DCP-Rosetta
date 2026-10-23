from hermax.model import Model


def build(instance):
    fixed_costs = instance["fixed_costs"]
    shipping_costs = instance["shipping_costs"]
    demands = instance["demands"]
    max_shipping = instance["max_shipping"]

    num_warehouses = 4
    num_regions = 3

    m = Model()

    # open_warehouse[i] = True if warehouse i is open
    open_warehouse = m.bool_vector("open_warehouse", num_warehouses)

    # ships[i][j] = units shipped from warehouse i to region j
    ships = m.int_matrix("ships", num_warehouses, num_regions, 0, max_shipping)

    # Constraint 1: If NY (0) is open, then LA (1) must be open
    m &= (open_warehouse[0] <= open_warehouse[1])

    # Constraint 2: At most 3 warehouses can be open
    m &= (sum(open_warehouse) <= 3)

    # Constraint 3: Either Atlanta (3) or LA (1) must be open
    m &= (open_warehouse[1] + open_warehouse[3] >= 1)

    # Constraint 4: Meet regional demands
    for j in range(num_regions):
        m &= (sum(ships[i][j] for i in range(num_warehouses)) == demands[j])

    # Constraint 5: Can only ship from open warehouses
    for i in range(num_warehouses):
        for j in range(num_regions):
            # If warehouse i is not open, ships[i][j] must be 0
            # This is encoded as: ships[i][j] <= max_shipping * open_warehouse[i]
            m &= (ships[i][j] <= max_shipping * open_warehouse[i])

    # Objective: minimize total cost
    # Total cost = sum of fixed costs for open warehouses + sum of shipping costs
    total_cost = sum(fixed_costs[i] * open_warehouse[i] for i in range(num_warehouses))
    total_cost += sum(shipping_costs[i][j] * ships[i][j] for i in range(num_warehouses) for j in range(num_regions))

    m.obj += total_cost

    return m, {"open_warehouse": open_warehouse, "ships": ships, "total_cost": total_cost}
