# flowshop_scheduling: a Gurobi (Python) model from DCP Rosetta.
# Download the `flowshop_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python flowshop_scheduling.py flowshop_scheduling.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Permutation flow shop: put the jobs in one order, each passing through the machines 1 to M in turn, so that the last job leaves the last machine as early as possible."""
    n_jobs = len(instance["jobs"])          # one position in the sequence per job
    n_machines = len(instance["machines"])  # the machines, in the order every job visits them
    p = instance["process_time"]            # p[j][m]: the time job j takes on machine m
    jobs = range(n_jobs)
    slots = range(n_jobs)                   # positions in the sequence, first to last
    machines = range(n_machines)
    # Not from the statement: the total of all processing times bounds every start and end time
    # (running the jobs one after another finishes within it). It keeps the time variables finite.
    horizon = sum(sum(row) for row in p)

    model = gp.Model("flowshop_scheduling")

    # job_at[k, j] is 1 when job j is the k-th job of the sequence, and 0 when not.
    job_at = model.addVars(slots, jobs, vtype=GRB.BINARY, name="job_at")
    # Each position in the sequence holds exactly one job.
    model.addConstrs((job_at.sum(k, "*") == 1 for k in slots), name="one_job_per_position")
    # Each job takes exactly one position in the sequence.
    model.addConstrs((job_at.sum("*", j) == 1 for j in jobs), name="one_position_per_job")

    # start[k, m] and end[k, m] are the times the k-th job of the sequence starts and finishes on machine m.
    start = model.addVars(slots, machines, lb=0, ub=horizon, vtype=GRB.INTEGER, name="start")
    end = model.addVars(slots, machines, lb=0, ub=horizon, vtype=GRB.INTEGER, name="end")
    # The k-th job takes its processing time on machine m, so it finishes that long after it starts.
    model.addConstrs((end[k, m] == start[k, m] + gp.quicksum(p[j][m] * job_at[k, j] for j in jobs)
                      for k in slots for m in machines), name="duration")
    # A job starts on machine m only after it has finished on machine m - 1.
    model.addConstrs((start[k, m] >= end[k, m - 1] for k in slots for m in machines if m > 0), name="route")
    # The k-th job starts on machine m only after the job before it has left machine m.
    model.addConstrs((start[k, m] >= end[k - 1, m] for k in slots for m in machines if k > 0),
                     name="machine_free")

    # The makespan is the time the last job leaves the last machine: the latest end time over all jobs and machines.
    makespan = model.addVar(lb=0, ub=horizon, vtype=GRB.INTEGER, name="makespan")
    model.addConstr(makespan == gp.max_([end[k, m] for k in slots for m in machines]), name="makespan_def")

    # Minimise the makespan: the time when all jobs have been processed.
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
