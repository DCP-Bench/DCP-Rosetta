# assignment_costs: a Gurobi (Python) model from DCP Rosetta.
# Download the `assignment_costs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python assignment_costs.py assignment_costs.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Assign people to tasks, each task to exactly one person and each person to at most one task, at the least total cost."""
    cost = instance["cost"]  # cost[i][j]: the cost of person j doing task i
    tasks = range(len(cost))        # the tasks are the rows of the cost table
    people = range(len(cost[0]))    # the people are the columns of the cost table

    model = gp.Model("assignment_costs")

    # x[i, j] is 1 when task i is assigned to person j, and 0 when not.
    x = model.addVars(tasks, people, vtype=GRB.BINARY, name="x")

    # Each task is assigned to exactly one person (x.sum(i, "*") adds x[i, j] over all people j).
    for i in tasks:
        model.addConstr(x.sum(i, "*") == 1, name=f"task[{i}]")

    # Each person takes at most one task (x.sum("*", j) adds x[i, j] over all tasks i).
    for j in people:
        model.addConstr(x.sum("*", j) <= 1, name=f"person[{j}]")

    # The objective: the total cost of the assignment, to be minimised.
    model.setObjective(gp.quicksum(cost[i][j] * x[i, j] for i in tasks for j in people), GRB.MINIMIZE)

    return model, {"x": [[x[i, j] for j in people] for i in tasks]}


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
