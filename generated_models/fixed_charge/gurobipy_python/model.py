# fixed_charge: a Gurobi (Python) model from DCP Rosetta.
# Download the `fixed_charge.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python fixed_charge.py fixed_charge.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """A company makes shirts, shorts and pants, each needing labour and cloth, and each can be made only on a rented machine: choose which machines to rent and how much of each product to make, to maximise the profit after the rent."""
    machines = instance["machines"]  # machine indices, 0 to num_machines - 1
    products = instance["products"]  # product indices: 0 shirts, 1 shorts, 2 pants
    resources = instance["resources"]  # resource indices: 0 labour hours, 1 cloth
    renting_cost = instance["renting_cost"]  # renting_cost[m]: the rent for machine m
    capacity = instance["capacity"]  # capacity[r]: the amount of resource r available
    product = instance["product"]  # product[p] = [profit per unit of p, the machine p needs]
    use = instance["use"]  # use[p][r]: the amount of resource r that one unit of p needs
    # The most of any one product that can be made, taken from the data (the largest capacity). The
    # statement sets no limit; it cannot cut off a plan, because every unit of a product uses at least
    # one unit of some resource, so no more than the largest capacity can be made.
    max_production = instance["max_production"]

    model = gp.Model("fixed_charge")

    # rent[m] is 1 when machine m is rented, and 0 when not.
    rent = model.addVars(machines, vtype=GRB.BINARY, name="rent")
    # produce[p] is how many of product p are made: a whole number from 0 to max_production.
    produce = model.addVars(products, lb=0, ub=max_production, vtype=GRB.INTEGER, name="produce")

    # The products use no more of each resource than its capacity (labour hours and cloth).
    model.addConstrs((gp.quicksum(use[p][r] * produce[p] for p in products) <= capacity[r]
                      for r in resources), name="capacity")

    # A product is made only on a rented machine: nothing is made unless its machine is rented
    # (max_production is the upper bound of produce[p], so it is a valid big-M).
    model.addConstrs((produce[p] <= max_production * rent[product[p][1]] for p in products),
                     name="machine")

    # z is the profit: the money from the products minus the rent of the machines.
    # It is at least 0, which the statement does not say: renting nothing earns 0, so the best profit is never negative.
    z = model.addVar(lb=0, vtype=GRB.INTEGER, name="z")
    model.addConstr(z == gp.quicksum(product[p][0] * produce[p] for p in products)
                    - gp.quicksum(renting_cost[m] * rent[m] for m in machines), name="profit")

    # Objective: maximise the profit.
    model.setObjective(z, GRB.MAXIMIZE)

    return model, {"z": z}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.Params.MIPGap = 0  # prove the optimum; the default stops within 0.01% of it
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a proven optimum
        print("Objective value:", round(model.ObjVal))
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
