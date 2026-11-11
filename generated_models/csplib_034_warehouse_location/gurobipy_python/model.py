# csplib_034_warehouse_location: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_034_warehouse_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_034_warehouse_location.py csplib_034_warehouse_location.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Open some of the candidate warehouses and assign every store to one open warehouse, without any warehouse supplying more stores than its capacity, so that the maintenance cost of the open warehouses plus the supply costs is as small as possible."""
    n_suppliers = instance["n_suppliers"]  # the number of candidate warehouses
    n_stores = instance["n_stores"]  # the number of stores to supply
    building_cost = instance["building_cost"]  # the maintenance cost of one open warehouse
    capacity = instance["capacity"]  # capacity[w]: the most stores warehouse w can supply
    cost = instance["cost_matrix"]  # cost[s][w]: the cost of supplying store s from warehouse w
    stores = range(n_stores)
    warehouses = range(n_suppliers)

    model = gp.Model("warehouse_location")

    # assign[s, w] is 1 when warehouse w supplies store s, and 0 when not
    assign = model.addVars(stores, warehouses, vtype=GRB.BINARY, name="assign")
    # opened[w] is 1 when warehouse w is open, and 0 when it is closed
    opened = model.addVars(warehouses, vtype=GRB.BINARY, name="open")

    # Each store is supplied by exactly one warehouse.
    model.addConstrs((assign.sum(s, "*") == 1 for s in stores), name="supplied")

    # A warehouse supplies stores only when it is open, and no more than its capacity of them.
    model.addConstrs((assign.sum("*", w) <= capacity[w] * opened[w] for w in warehouses),
                     name="capacity")

    # Total cost: the supply cost of every store plus the maintenance of every open warehouse.
    total_cost = gp.quicksum(cost[s][w] * assign[s, w] for s in stores for w in warehouses) \
        + building_cost * opened.sum()
    model.setObjective(total_cost, GRB.MINIMIZE)

    # supplier_assignment[s]: the warehouse (numbered from 0) that supplies store s
    supplier_assignment = [gp.quicksum(w * assign[s, w] for w in warehouses) for s in stores]
    return model, {
        "total_cost": total_cost,
        "open_warehouses": [opened[w] for w in warehouses],
        "supplier_assignment": supplier_assignment,
    }


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
