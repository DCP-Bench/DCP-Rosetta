# jobshop: a Gurobi (Python) model from DCP Rosetta.
# Download the `jobshop.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python jobshop.py jobshop.json

from itertools import combinations

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Schedule the tasks of each job in their given order, each on its machine, with no two tasks on one machine at the same time, so that the last task finishes as early as possible."""
    jobs_data = instance["jobs_data"]  # jobs_data[j][t] = [machine, duration] of task t of job j
    tasks = [(j, t) for j, job in enumerate(jobs_data) for t in range(len(job))]
    # Not in the statement: the total of all task durations. Running the tasks one after another
    # never takes longer, so no time needs to exceed it; the bound keeps every time finite.
    horizon = sum(duration for job in jobs_data for _, duration in job)

    model = gp.Model("jobshop")

    # start[j, t] and end[j, t] are the times when task t of job j starts and ends
    start = model.addVars(tasks, lb=0, ub=horizon, vtype=GRB.INTEGER, name="start")
    end = model.addVars(tasks, lb=0, ub=horizon, vtype=GRB.INTEGER, name="end")

    # A task, once started, runs for its full duration.
    model.addConstrs((end[j, t] == start[j, t] + jobs_data[j][t][1] for j, t in tasks),
                     name="duration")

    # No task starts before the previous task of its job has ended.
    model.addConstrs((start[j, t] >= end[j, t - 1] for j, t in tasks if t > 0), name="precedence")

    # A machine works on one task at a time. For each pair of tasks on the same machine, first[a, b]
    # is 1 when task a runs before task b, and 0 when b runs before a; each order is an indicator
    # constraint, so no big-M is needed.
    machines = sorted({m for job in jobs_data for m, _ in job})
    on = {m: [(j, t) for j, t in tasks if jobs_data[j][t][0] == m] for m in machines}
    pairs = [(a, b) for m in machines for a, b in combinations(on[m], 2)]
    first = model.addVars(pairs, vtype=GRB.BINARY, name="first")
    model.addConstrs(((first[a, b] == 1) >> (start[b] >= end[a]) for a, b in pairs),
                     name="a_before_b")
    model.addConstrs(((first[a, b] == 0) >> (start[a] >= end[b]) for a, b in pairs),
                     name="b_before_a")

    # makespan: the time at which the last task ends, which is what is minimised
    makespan = model.addVar(lb=0, ub=horizon, vtype=GRB.INTEGER, name="makespan")
    model.addConstr(makespan == gp.max_([end[k] for k in tasks]), name="makespan_def")
    model.setObjective(makespan, GRB.MINIMIZE)

    return model, {"makespan": makespan}


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
