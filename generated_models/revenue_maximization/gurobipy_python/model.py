# revenue_maximization: a Gurobi (Python) model from DCP Rosetta.
# Download the `revenue_maximization.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python revenue_maximization.py revenue_maximization.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Airline revenue: choose how many units of each itinerary package to sell, so that no flight leg
    is overbooked and the total revenue is as large as possible."""
    seats = instance["available_seats"]  # seats[j]: the passenger seats on flight leg j
    demand = instance["demand"]  # demand[i]: the estimated demand for package i
    revenue = instance["revenue"]  # revenue[i]: the price of one unit of package i
    uses = instance["delta"]  # uses[i][j] is 1 when package i flies on leg j, 0 when not
    packages = range(len(demand))  # the itinerary packages
    legs = range(len(seats))  # the one-way non-stop flight legs

    model = gp.Model("revenue_maximization")

    # packages_to_sell[i] is the number of units of package i to sell. The upper bound is the estimated
    # demand for the package (a cap taken from the data: the statement gives the demand, not the cap in words).
    packages_to_sell = model.addVars(packages, lb=0, ub=demand, vtype=GRB.INTEGER, name="packages_to_sell")

    # Each unit of a package reserves a seat on every leg it flies, so on each leg the seats reserved
    # by the packages sold are no more than the seats available.
    model.addConstrs((gp.quicksum(uses[i][j] * packages_to_sell[i] for i in packages) <= seats[j]
                      for j in legs), name="seats")

    # The total revenue: the price of each package times the units sold, summed over the packages.
    max_revenue = gp.quicksum(revenue[i] * packages_to_sell[i] for i in packages)
    model.setObjective(max_revenue, GRB.MAXIMIZE)

    return model, {"packages_to_sell": [packages_to_sell[i] for i in packages],
                   "max_revenue": max_revenue}


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
