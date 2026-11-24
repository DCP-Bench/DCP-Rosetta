# covering_opl: a Gurobi (Python) model from DCP Rosetta.
# Download the `covering_opl.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python covering_opl.py covering_opl.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Choose a set of workers who can together perform every task, at the least total hiring
    cost. Each worker is qualified for certain tasks and has a hiring cost."""
    cost = instance["Cost"]  # cost[w]: the hiring cost of worker w (0-based)
    qualified = instance["Qualified"]  # qualified[t]: the workers, 1-based, who can do task t
    workers = range(instance["nb_workers"])  # the workers, numbered 0 to nb_workers - 1
    tasks = range(instance["num_tasks"])  # the tasks, numbered 0 to num_tasks - 1

    model = gp.Model("covering_opl")

    # hire[w] is 1 when worker w is hired, and 0 when not.
    hire = model.addVars(workers, vtype=GRB.BINARY, name="workers")

    # Every task has at least one hired worker qualified for it. The list is 1-based, so worker
    # w in it is hire[w - 1].
    model.addConstrs((gp.quicksum(hire[w - 1] for w in qualified[t]) >= 1 for t in tasks),
                     name="task")

    # The total hiring cost of the hired workers.
    total_cost = gp.quicksum(cost[w] * hire[w] for w in workers)
    # Minimise the total hiring cost.
    model.setObjective(total_cost, GRB.MINIMIZE)

    return model, {"total_cost": total_cost, "workers": [hire[w] for w in workers]}


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
