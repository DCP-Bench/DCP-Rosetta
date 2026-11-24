# multi: a PyCSP3 model from DCP Rosetta.
# Download the `multi.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python multi.py multi.json

from pycsp3 import *


def create_model(instance):
    """Multi-commodity transportation: each origin has a supply of each product, each destination
    a demand for each product, and shipping one unit of a product from an origin to a destination
    has a cost. Ship all products from the origins to the destinations at minimum total cost."""
    supply = instance["supply"]  # supply[i][p]: units of product p available at origin i
    demand = instance["demand"]  # demand[j][p]: units of product p required at destination j
    limit = instance["limit"]    # limit[i][j]: most units, of all products together, sent from origin i to destination j
    cost = instance["cost"]      # cost[i][j][p]: cost of shipping one unit of product p from origin i to destination j
    n_origins = len(supply)
    n_destinations = len(demand)
    n_products = len(supply[0])

    # The ways to split `units` units among `n_parts` origins, as tuples of one quantity per origin.
    def splits(units, n_parts):
        if n_parts == 1:
            return [(units,)]
        return [(first,) + rest for first in range(units + 1) for rest in splits(units - first, n_parts - 1)]

    # shipped[i][j][p] is the number of units of product p sent from origin i to destination j. A shipment
    # is at most the lane limit, so at most the largest limit (quantities taken as non-negative).
    largest_limit = max(max(row) for row in limit)
    shipped = VarArray(size=[n_origins, n_destinations, n_products], dom=range(largest_limit + 1))

    # delivery_cost[j][p] is the cost of shipping the units of product p that destination j receives. Costs are
    # taken as non-negative and exactly the demand is delivered, so it is at most the largest unit cost times the demand.
    largest_cost = max(c for origin in cost for lane in origin for c in lane)
    delivery_cost = VarArray(size=[n_destinations, n_products],
                             dom=lambda j, p: range(largest_cost * demand[j][p] + 1))

    # total_cost is the total shipping cost, at most the largest unit cost times the total demand (costs
    # taken as non-negative, every unit delivered is shipped once).
    total_demand = sum(sum(row) for row in demand)
    total_cost = Var(dom=range(largest_cost * total_demand + 1))

    satisfy(
        # Each destination receives exactly its demand of each product, and pays for it. This is one table
        # per destination and product that lists the splits of the demand among the origins with their cost; it
        # restates the demand and cost equations jointly, which lets ACE prove the optimum within the time limit
        # (separate sums leave the cost bound too weak to prove optimality on the largest instance). The table has one
        # row per split, so it grows quickly with the demand and the number of origins; it is practical for instances of
        # the size in the benchmark.
        [Table(scope=list(shipped[:, j, p]) + [delivery_cost[j][p]],
               supports=[units + (sum(cost[i][j][p] * units[i] for i in range(n_origins)),)
                         for units in splits(demand[j][p], n_origins)])
         for j in range(n_destinations) for p in range(n_products)],
        # Each origin ships no more of each product than its supply of it.
        [Sum(shipped[i, :, p]) <= supply[i][p] for i in range(n_origins) for p in range(n_products)],
        # The units of all products sent on a lane stay within its limit (an instance field, not in the statement's text).
        [Sum(shipped[i][j]) <= limit[i][j] for i in range(n_origins) for j in range(n_destinations)],
        # The total cost is the cost of the deliveries.
        total_cost == Sum(delivery_cost),
    )

    # Minimise the total shipping cost.
    minimize(total_cost)

    return {"total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
