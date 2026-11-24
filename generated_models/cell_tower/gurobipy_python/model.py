# cell_tower: a Gurobi (Python) model from DCP Rosetta.
# Download the `cell_tower.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python cell_tower.py cell_tower.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Cell towers: choose which candidate sites to build towers on, within the budget, so that as many people as possible are covered."""
    delta = instance["delta"]  # delta[i][j] is 1 if a tower at site i covers region j
    cost = instance["cost"]  # cost[i] is the cost of building a tower at site i
    population = instance["population"]  # population[j] is the number of inhabitants of region j
    budget = instance["budget"]  # the most money that may be spent on towers
    sites = range(len(cost))  # the candidate tower sites
    regions = range(len(population))  # the regions of the city to cover

    model = gp.Model("cell_tower")

    # build_tower[i] is 1 when a tower is built at site i;
    # covered[j] is 1 when region j counts as covered.
    build_tower = model.addVars(sites, vtype=GRB.BINARY, name="build_tower")
    covered = model.addVars(regions, vtype=GRB.BINARY, name="covered")

    # A region is covered only if at least one tower that covers it is built.
    model.addConstrs((covered[j] <= gp.quicksum(delta[i][j] * build_tower[i] for i in sites)
                      for j in regions), name="coverage")

    # The towers built cost no more than the budget.
    model.addConstr(gp.quicksum(cost[i] * build_tower[i] for i in sites) <= budget, name="budget")

    # Provide coverage to as many people as possible: maximise the population of the covered regions.
    total_population_covered = gp.quicksum(population[j] * covered[j] for j in regions)
    model.setObjective(total_population_covered, GRB.MAXIMIZE)

    return model, {"build_tower": [build_tower[i] for i in sites],
                   "total_population_covered": total_population_covered}


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
