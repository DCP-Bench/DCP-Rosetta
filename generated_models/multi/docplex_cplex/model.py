# multi: a CPLEX (Python) model from DCP Rosetta.
# Download the `multi.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python multi.py multi.json

from docplex.mp.model import Model


def create_model(instance):
    """Multi-commodity transportation: ship every product from origins to destinations at the least total cost."""
    supply = instance["supply"]  # supply[i][p]: units of product p at origin i
    demand = instance["demand"]  # demand[j][p]: units of product p destination j needs
    limit = instance["limit"]    # limit[i][j]: most units, all products together, from i to j
    cost = instance["cost"]      # cost[i][j][p]: cost of shipping one unit of p from i to j
    origins = range(len(supply))
    destinations = range(len(demand))
    goods = range(len(supply[0]))

    # Bounds that keep the variables finite without cutting off a solution: a shipment never
    # exceeds the largest supply, and the total cost never exceeds all the supply shipped at
    # the dearest rate.
    max_supply = max(max(row) for row in supply)
    max_total_cost = sum(sum(row) for row in supply) * max(max(row) for matrix in cost for row in matrix)

    model = Model("multi")

    # x[i, j, p] is the amount of product p shipped from origin i to destination j.
    x = model.integer_var_cube(origins, destinations, goods, 0, max_supply, name="x")

    # No origin ships more of a product than it has.
    model.add_constraints(model.sum(x[i, j, p] for j in destinations) <= supply[i][p]
                          for i in origins for p in goods)

    # Every destination receives at least the demand for each product.
    model.add_constraints(model.sum(x[i, j, p] for i in origins) >= demand[j][p]
                          for j in destinations for p in goods)

    # The total shipped on each route stays within its limit.
    model.add_constraints(model.sum(x[i, j, p] for p in goods) <= limit[i][j]
                          for i in origins for j in destinations)

    # total_cost is the cost of all shipments; a variable of its own so that the
    # declared output is this one integer rather than every shipment behind it.
    total_cost = model.integer_var(0, max_total_cost, name="total_cost")
    model.add_constraint(total_cost == model.sum(cost[i][j][p] * x[i, j, p]
                                                 for i in origins for j in destinations for p in goods),
                         ctname="cost")

    # Minimise the shipping cost.
    model.minimize(total_cost)

    return model, {"total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
