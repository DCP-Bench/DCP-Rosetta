# multi: a Gurobi (Python) model from DCP Rosetta.
# Download the `multi.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python multi.py multi.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Multi-commodity transportation: ship every product from the origins to the destinations so that the total shipping cost is as small as possible."""
    supply = instance["supply"]  # supply[i][p]: units of product p at origin i
    demand = instance["demand"]  # demand[j][p]: units of product p destination j needs
    limit = instance["limit"]    # limit[i][j]: most units, all products together, from i to j
    cost = instance["cost"]      # cost[i][j][p]: cost of shipping one unit of p from i to j
    origins = range(len(supply))
    destinations = range(len(demand))
    goods = range(len(supply[0]))

    model = gp.Model("multi")

    # Not in the problem statement: no shipment exceeds the largest supply. The supply
    # constraints already imply this bound; it keeps every shipment variable finite.
    max_supply = max(max(row) for row in supply)

    # x[i, j, p] is the number of units of product p shipped from origin i to destination j.
    # Not in the problem statement: the units are whole numbers (the reference uses integers).
    x = model.addVars(origins, destinations, goods, ub=max_supply, vtype=GRB.INTEGER, name="x")

    # Every origin ships no more of each product than it has.
    model.addConstrs((x.sum(i, "*", p) <= supply[i][p] for i in origins for p in goods), name="supply")

    # Every destination receives at least its demand for each product.
    model.addConstrs((x.sum("*", j, p) >= demand[j][p] for j in destinations for p in goods), name="demand")

    # Not in the problem statement: the total of all products shipped on each route stays within the route's limit.
    model.addConstrs((x.sum(i, j, "*") <= limit[i][j] for i in origins for j in destinations), name="limit")

    # Not in the problem statement: the total cost is at most all supply shipped at the dearest rate.
    max_total_cost = sum(sum(row) for row in supply) * max(max(row) for matrix in cost for row in matrix)

    # total_cost is the total shipping cost. It is one variable, not the expression over every
    # shipment, so that the declared output is a single integer: the solver's enumeration of
    # further solutions then only has to rule out one value.
    total_cost = model.addVar(ub=max_total_cost, vtype=GRB.INTEGER, name="total_cost")
    # The total shipping cost: each shipment's units times the cost of one unit of that product on that route.
    model.addConstr(total_cost == gp.quicksum(cost[i][j][p] * x[i, j, p]
                                              for i in origins for j in destinations for p in goods),
                    name="cost")

    # Minimise the total shipping cost.
    model.setObjective(total_cost, GRB.MINIMIZE)

    return model, {"total_cost": total_cost}


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
