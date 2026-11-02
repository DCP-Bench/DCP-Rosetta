# multi: a hermax (Python) model from DCP Rosetta.
# Download the `multi.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
# Then run it on the first instance (after `pip install hermax`):
#   python multi.py multi.json

from hermax.model import Model, sum_expr


def create_model(instance):
    """Ship several products from origins to destinations so that every destination
    receives its demand of each product, no origin ships more of a product than its
    supply, no lane carries more than its limit, and the total shipping cost is as
    small as possible."""
    supply = instance["supply"]  # supply[i][p]: units of product p available at origin i
    demand = instance["demand"]  # demand[j][p]: units of product p needed at destination j
    limit = instance["limit"]  # limit[i][j]: most units, all products together, on the lane from i to j
    cost = instance["cost"]  # cost[i][j][p]: cost of shipping one unit of product p from i to j
    n_origins = len(supply)
    n_destinations = len(demand)
    n_products = len(supply[0])

    m = Model()

    # shipped[i][j][p] is the number of units of product p sent from origin i to destination j.
    # Its upper bound is the smaller of the origin's supply of p and the lane limit.
    shipped = [[[m.int(f"shipped_{i}_{j}_{p}", 0, min(supply[i][p], limit[i][j]))
                 for p in range(n_products)]
                for j in range(n_destinations)]
               for i in range(n_origins)]

    # Supply: each origin ships at most its supply of each product.
    for i in range(n_origins):
        for p in range(n_products):
            m &= (sum(shipped[i][j][p] for j in range(n_destinations)) <= supply[i][p])

    # Demand: each destination receives its demand of each product. Every unit costs
    # something to ship, so a cheapest plan never sends more than the demand: asking
    # for exactly the demand loses no optimal plan, and the objective below relies on it.
    for j in range(n_destinations):
        for p in range(n_products):
            m &= (sum(shipped[i][j][p] for i in range(n_origins)) == demand[j][p])

    # Lane limit: all products together on the lane from origin i to destination j stay within limit[i][j].
    for i in range(n_origins):
        for j in range(n_destinations):
            m &= (sum(shipped[i][j][p] for p in range(n_products)) <= limit[i][j])

    # total_cost is the cost of all shipments: each unit shipped costs its unit cost on that lane.
    total_cost = sum_expr(cost[i][j][p] * shipped[i][j][p]
                          for i in range(n_origins)
                          for j in range(n_destinations)
                          for p in range(n_products))

    # Minimise the total shipping cost. cheapest[j][p] is the lowest unit cost of getting
    # product p to destination j from any origin; every plan pays at least that for each
    # of the demand[j][p] units. Since exactly the demand is delivered, the total cost is
    # that fixed amount (shift) plus what each unit costs above its cheapest origin, so the
    # solver is given only those extra costs plus the constant. This is the same objective,
    # written so the solver weighs far fewer soft clauses: one instance took over 180 s
    # with the plain total and 13 s with this form. total_cost is reported as the plain sum.
    cheapest = [[min(cost[i][j][p] for i in range(n_origins)) for p in range(n_products)]
                for j in range(n_destinations)]
    shift = sum(cheapest[j][p] * demand[j][p]
                for j in range(n_destinations) for p in range(n_products))
    m.obj += shift + sum_expr((cost[i][j][p] - cheapest[j][p]) * shipped[i][j][p]
                              for i in range(n_origins)
                              for j in range(n_destinations)
                              for p in range(n_products))

    return m, {"total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
