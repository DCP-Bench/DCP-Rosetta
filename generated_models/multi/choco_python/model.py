# multi: a Choco-solver (Python) model from DCP Rosetta.
# Download the `multi.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python multi.py multi.json

from pychoco.model import Model


def delivery_plans(units, caps, unit_costs):
    """Every way to ship exactly `units` units of one product to one destination.

    Origin i ships between 0 and caps[i] units at unit_costs[i] each. A plan is the list
    of shipments from the origins followed by their total cost.
    """
    plans = []

    def extend(origin, left, shipped):
        if origin == len(caps):
            if left == 0:
                plans.append(shipped + [sum(c * v for c, v in zip(unit_costs, shipped))])
            return
        for amount in range(min(caps[origin], left) + 1):
            extend(origin + 1, left - amount, shipped + [amount])

    extend(0, units, [])
    return plans


def create_model(instance):
    """Multi-commodity transportation: ship products from origins to destinations so
    that every destination gets its demand of each product, no origin ships more of a
    product than its supply, and no route carries more than its limit, at the lowest
    total shipping cost."""
    supply = instance["supply"]  # supply[i][p]: units of product p available at origin i
    demand = instance["demand"]  # demand[j][p]: units of product p needed at destination j
    limit = instance["limit"]    # limit[i][j]: most units that can go from origin i to destination j
    cost = instance["cost"]      # cost[i][j][p]: cost of shipping one unit of product p from origin i to destination j
    n_origins = len(supply)
    n_destinations = len(demand)
    n_products = len(supply[0])

    # The most the whole supply could cost, at the dearest unit price.
    max_total_cost = sum(sum(row) for row in supply) * max(max(row) for matrix in cost for row in matrix)

    # Shipping costs are not negative, so an optimal plan delivers exactly each demand.
    assert min(c for matrix in cost for row in matrix for c in row) >= 0, "shipping costs must not be negative"

    model = Model()

    # most[i][j][p]: the most units of product p that can go from origin i to destination j
    most = [[[min(supply[i][p], limit[i][j], demand[j][p]) for p in range(n_products)]
             for j in range(n_destinations)] for i in range(n_origins)]
    # x[i][j][p]: units of product p shipped from origin i to destination j
    x = [[[model.intvar(0, most[i][j][p], name=f"x_{i}_{j}_{p}") for p in range(n_products)]
          for j in range(n_destinations)] for i in range(n_origins)]

    # Each destination gets exactly its demand of each product. The shipments for a
    # destination and product must follow one way of splitting that demand among the
    # origins, and the cost of the split is the delivery cost. Listing the splits up
    # front gives the search a tight bound on each delivery cost.
    # delivery_cost: the delivery cost of each destination and product
    delivery_cost = []
    for j in range(n_destinations):
        for p in range(n_products):
            shipments = [x[i][j][p] for i in range(n_origins)]
            plans = delivery_plans(demand[j][p], [most[i][j][p] for i in range(n_origins)],
                                   [cost[i][j][p] for i in range(n_origins)])
            cost_jp = model.intvar(min(plan[-1] for plan in plans), max(plan[-1] for plan in plans),
                                   name=f"delivery_cost_{j}_{p}")
            model.table(shipments + [cost_jp], plans).post()
            delivery_cost.append(cost_jp)

    # An origin ships no more of a product than its supply.
    for i in range(n_origins):
        for p in range(n_products):
            model.sum([x[i][j][p] for j in range(n_destinations)], "<=", supply[i][p]).post()

    # The units of all products on each route from an origin to a destination stay within its limit.
    for i in range(n_origins):
        for j in range(n_destinations):
            model.sum(x[i][j], "<=", limit[i][j]).post()

    # total_cost: the total shipping cost of all deliveries, to be reported
    total_cost = model.intvar(0, max_total_cost, name="total_cost")
    model.sum(delivery_cost, "=", total_cost).post()

    # Minimise the total shipping cost.
    return model, {"total_cost": total_cost}, {"objective": total_cost, "maximize": False}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
