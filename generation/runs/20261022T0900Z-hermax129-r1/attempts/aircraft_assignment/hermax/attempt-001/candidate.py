from hermax.model import Model


def build(instance):
    # Extract instance data
    availability = instance["availability"]
    capabilities = instance["capabilities"]
    costs = instance["costs"]
    demand = instance["demand"]

    num_types = len(availability)
    num_routes = len(demand)

    # Create the model
    m = Model()

    # Decision variables: allocation[i][j] = number of aircraft of type i assigned to route j
    allocation = m.int_matrix("allocation", num_types, num_routes, 0, max(availability))

    # Constraint 1: Demand satisfaction - total capacity on each route >= demand
    # For each route j: sum_i(allocation[i][j] * capabilities[i][j]) >= demand[j]
    for j in range(num_routes):
        m &= (sum(allocation[i][j] * capabilities[i][j] for i in range(num_types)) >= demand[j])

    # Constraint 2: Availability limits - total allocated of each type <= availability
    # For each type i: sum_j(allocation[i][j]) <= availability[i]
    for i in range(num_types):
        m &= (sum(allocation[i][j] for j in range(num_routes)) <= availability[i])

    # Objective: Minimize total cost
    # sum_i,j(allocation[i][j] * costs[i][j])
    # Linear expression of IntVars in the objective (no auxiliary variable needed)
    m.obj += sum(allocation[i][j] * costs[i][j] for i in range(num_types) for j in range(num_routes))

    return m, {"allocation": allocation}
