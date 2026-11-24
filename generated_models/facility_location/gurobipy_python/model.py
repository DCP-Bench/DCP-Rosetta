# facility_location: a Gurobi (Python) model from DCP Rosetta.
# Download the `facility_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/facility_location.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python facility_location.py facility_location.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Facility location: open warehouses and ship to regions at the least weekly cost, under three opening rules."""
    fixed_costs = instance["fixed_costs"]          # fixed_costs[i]: the cost of opening warehouse i
    shipping_costs = instance["shipping_costs"]    # shipping_costs[i][j]: per unit, warehouse i to region j
    demands = instance["demands"]                  # demands[j]: the units region j needs each week
    max_shipping = instance["max_shipping"]        # the most units one warehouse can ship each week
    warehouses = range(len(instance["warehouse_s"]))  # the four candidate warehouses
    regions = range(len(demands))
    # The warehouses are, in order, New York, Los Angeles, Chicago and Atlanta.
    # Chicago appears in no rule, so its index is not named.
    new_york, los_angeles, _, atlanta = warehouses

    model = gp.Model("facility_location")

    # open_warehouse[i] is 1 when warehouse i is open; ships[i, j] is the units
    # it sends to region j each week.
    open_warehouse = model.addVars(warehouses, vtype=GRB.BINARY, name="open_warehouse")
    ships = model.addVars(warehouses, regions, lb=0, ub=max_shipping, vtype=GRB.INTEGER, name="ships")

    # A warehouse ships at most max_shipping units a week, and nothing when closed.
    model.addConstrs((ships.sum(i, "*") <= max_shipping * open_warehouse[i] for i in warehouses),
                     name="shipping")

    # Every region receives at least its weekly demand.
    model.addConstrs((ships.sum("*", j) >= demands[j] for j in regions), name="demand")

    # 1. If the New York warehouse is opened, the Los Angeles one is opened too.
    model.addConstr(open_warehouse[new_york] <= open_warehouse[los_angeles], name="new_york_needs_la")
    # 2. At most three warehouses are open.
    model.addConstr(open_warehouse.sum() <= 3, name="at_most_three")
    # 3. The Atlanta or the Los Angeles warehouse is open.
    model.addConstr(open_warehouse[atlanta] + open_warehouse[los_angeles] >= 1, name="atlanta_or_la")

    # total_cost is the fixed cost of the open warehouses plus the shipping cost.
    # The bound 10000 is not in the statement: it is the domain the reference model
    # gives total_cost, kept so that the variable is finite.
    total_cost = model.addVar(lb=0, ub=10000, vtype=GRB.INTEGER, name="total_cost")
    model.addConstr(total_cost == gp.quicksum(fixed_costs[i] * open_warehouse[i] for i in warehouses)
                    + gp.quicksum(shipping_costs[i][j] * ships[i, j] for i in warehouses for j in regions),
                    name="cost")

    # Minimise the total cost.
    model.setObjective(total_cost, GRB.MINIMIZE)

    return model, {"total_cost": total_cost,
                   "open_warehouse": [open_warehouse[i] for i in warehouses],
                   "ships": [[ships[i, j] for j in regions] for i in warehouses]}


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
