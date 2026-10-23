from hermax.model import Model


def build(instance):
    """Fixed-charge manufacturing problem.

    Maximize sum(profit[i]*x[i]) - sum(renting_cost[i]*y[i]) subject to
    resource constraints and fixed-charge constraints.
    """
    num_products = instance["num_products"]
    num_machines = instance["num_machines"]

    profit = [instance["product"][i][0] for i in range(num_products)]
    use = instance["use"]
    resources = instance["resources"]
    capacity = instance["capacity"]
    max_production = instance["max_production"]
    renting_cost = instance["renting_cost"]

    model = Model()

    # Variables
    x = model.int_vector("x", num_products, 0, max_production)
    y = model.bool_vector("y", num_machines)

    # Resource capacity constraints
    for res_idx in range(len(resources)):
        total_usage = sum(use[i][res_idx] * x[i] for i in range(num_products))
        model &= (total_usage <= capacity[res_idx])

    # Fixed-charge constraints
    for i in range(num_products):
        model &= (x[i] <= max_production * y[i])

    # Objective: z = profit - renting
    z = model.sum_var(
        [profit[i] * x[i] for i in range(num_products)] +
        [-renting_cost[i] * y[i] for i in range(num_machines)],
        name="z"
    )

    return model, {"z": z}
