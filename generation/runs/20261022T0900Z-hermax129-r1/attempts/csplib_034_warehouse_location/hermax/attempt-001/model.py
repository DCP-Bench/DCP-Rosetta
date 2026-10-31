from hermax.model import Model


def build(instance):
    n_suppliers = instance["n_suppliers"]
    n_stores = instance["n_stores"]
    building_cost = instance["building_cost"]
    capacity = instance["capacity"]
    cost_matrix = instance["cost_matrix"]

    model = Model()

    # open_warehouses[i] = 1 if warehouse i is open
    open_warehouses = model.bool_vector("open", n_suppliers)

    # supplier_assignment[s] = warehouse that supplies store s
    supplier_assignment = model.int_vector("supplier", n_stores, 0, n_suppliers - 1)

    # Constraints:
    # 1. Each store must be assigned to exactly one warehouse
    #    (This is implicit in the variable definition)

    # 2. If store s is assigned to warehouse w, then warehouse w must be open
    for s in range(n_stores):
        for w in range(n_suppliers):
            # If supplier_assignment[s] == w, then open_warehouses[w] must be 1
            # Rewrite as: not (supplier_assignment[s] == w) or open_warehouses[w]
            # This is implemented as: supplier_assignment[s] != w or open_warehouses[w]
            # But we need to express this as a constraint

            # Actually, let's use a different approach:
            # Create auxiliary binary variables for assignment
            pass

    # Alternative approach: use assignment matrix
    # is_assigned[s][w] = 1 if store s is assigned to warehouse w
    is_assigned = model.bool_matrix("assigned", n_stores, n_suppliers)

    # Constraint: each store is assigned to exactly one warehouse
    for s in range(n_stores):
        model &= (sum(is_assigned[s][w] for w in range(n_suppliers)) == 1)

    # Constraint: if store s is assigned to warehouse w, then warehouse w is open
    for s in range(n_stores):
        for w in range(n_suppliers):
            # is_assigned[s][w] => open_warehouses[w]
            # not is_assigned[s][w] or open_warehouses[w]
            model &= (~is_assigned[s][w]) | open_warehouses[w]

    # Constraint: warehouse capacity
    for w in range(n_suppliers):
        # Number of stores assigned to warehouse w <= capacity[w]
        num_assigned = sum(is_assigned[s][w] for s in range(n_stores))
        model &= (num_assigned <= capacity[w])

    # Link supplier_assignment to is_assigned
    # supplier_assignment[s] = w if is_assigned[s][w] = 1
    for s in range(n_stores):
        for w in range(n_suppliers):
            # is_assigned[s][w] = 1 => supplier_assignment[s] = w
            # ~is_assigned[s][w] | (supplier_assignment[s] = w)
            # But we can't use equality in OR

            # Instead: supplier_assignment[s] = sum(w * is_assigned[s][w])
            # This is a linear constraint
            pass

    # Use: supplier_assignment[s] = sum(w * is_assigned[s][w] for w)
    for s in range(n_stores):
        model &= (supplier_assignment[s] == sum(w * is_assigned[s][w] for w in range(n_suppliers)))

    # Objective: minimize total cost
    # total_cost = building_cost * sum(open_warehouses) + sum(cost_matrix[s][supplier_assignment[s]])

    # Building cost contribution
    building_total = building_cost * sum(open_warehouses[w] for w in range(n_suppliers))

    # Supply cost contribution
    # supply_cost[s] = cost_matrix[s][supplier_assignment[s]]
    # But this requires indexing with a variable, which is complex
    # Alternative: supply_cost[s] = sum(is_assigned[s][w] * cost_matrix[s][w])

    supply_total = 0
    for s in range(n_stores):
        supply_cost_s = sum(cost_matrix[s][w] * is_assigned[s][w] for w in range(n_suppliers))
        supply_total += supply_cost_s

    total_cost_expr = building_total + supply_total

    # Objective: minimize total_cost_expr
    # For MaxSAT, we minimize by penalizing larger values
    max_cost = building_cost * n_suppliers + sum(max(row) for row in cost_matrix) * n_stores
    for cost_level in range(max_cost, -1, -1):
        model.obj[1] += (~(total_cost_expr < cost_level))

    # Return outputs
    # total_cost must be an integer output
    total_cost = model.int_vector("total_cost", 1, 0, max_cost)
    model &= (total_cost[0] == total_cost_expr)

    return model, {
        "open_warehouses": open_warehouses,
        "supplier_assignment": supplier_assignment,
        "total_cost": total_cost[0]
    }
