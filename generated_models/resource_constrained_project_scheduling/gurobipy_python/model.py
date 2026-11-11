# resource_constrained_project_scheduling: a Gurobi (Python) model from DCP Rosetta.
# Download the `resource_constrained_project_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python resource_constrained_project_scheduling.py resource_constrained_project_scheduling.json

import gurobipy as gp
from gurobipy import GRB


def serial_schedule(durations, needs, capacities, preds, order):
    """Start times of a feasible schedule: the jobs are taken in the given order, and each starts
    at the earliest time after its predecessors have finished at which every resource has room
    for its whole run."""
    used = {}
    start = {}
    for i in order:
        t = max((start[p] + durations[p] for p in preds[i]), default=0)
        while any(used.get((r, s), 0) + needs[i][r] > capacities[r]
                  for s in range(t, t + durations[i]) for r in range(len(capacities))):
            t += 1
        start[i] = t
        for s in range(t, t + durations[i]):
            for r in range(len(capacities)):
                used[r, s] = used.get((r, s), 0) + needs[i][r]
    return start


def create_model(instance):
    """Resource-constrained project scheduling: give each job a start time, after its predecessors have finished and within the resource capacities, so that the project finishes as early as possible."""
    durations = instance["durations_data"]            # durations[i]: how long job i runs
    needs = instance["resource_needs_data"]           # needs[i][r]: how much of resource r job i uses while it runs
    capacities = instance["resource_capacities_data"]  # capacities[r]: how much of resource r is available at any time
    links = instance["successors_link_data"]          # [a, b]: job a must finish before job b starts
    jobs = range(len(durations))
    resources = range(len(capacities))

    preds = {i: [a for a, b in links if b == i] for i in jobs}  # the jobs that must finish before job i starts
    succs = {i: [b for a, b in links if a == i] for i in jobs}  # the jobs that must start after job i finishes

    def ready(key):
        """The jobs in the order of key, but each only after its predecessors."""
        order = []
        while len(order) < len(jobs):
            order.append(next(i for i in sorted(jobs, key=key)
                              if i not in order and all(p in order for p in preds[i])))
        return order

    # head[i]: the earliest start of job i given only the precedences, the longest chain of durations before it.
    head = {}
    for i in ready(lambda i: i):
        head[i] = max((head[p] + durations[p] for p in preds[i]), default=0)
    # tail[i]: the longest chain of durations from the start of job i to the end of the chain,
    # job i included; the project lasts at least tail[i] after job i starts.
    tail = {}
    for i in reversed(ready(lambda i: i)):
        tail[i] = durations[i] + max((tail[j] for j in succs[i]), default=0)

    # Not in the statement: an upper bound on the optimal makespan, the finish time of a feasible
    # schedule built greedily from the instance, which is used only to limit the time grid. No
    # optimal schedule starts job i later than bound - tail[i], so no optimum is lost.
    # Time-indexed encoding (one binary per job and start time) so that the resource limits are
    # linear; the bound keeps the time grid, and so the model, small.
    bound = min(max(start[i] + durations[i] for i in jobs)
                for order in (ready(lambda i: (head[i], -tail[i], i)),
                              ready(lambda i: (-tail[i], head[i], i)))
                for start in [serial_schedule(durations, needs, capacities, preds, order)])

    model = gp.Model("rcpsp")

    # at[i, t] is 1 when job i starts at time t, for t from its earliest start to its latest start.
    window = {i: range(head[i], bound - tail[i] + 1) for i in jobs}
    at = model.addVars([(i, t) for i in jobs for t in window[i]], vtype=GRB.BINARY, name="at")
    # start[i] is the start time of job i.
    start = [gp.quicksum(t * at[i, t] for t in window[i]) for i in jobs]

    # Each job starts at exactly one time.
    model.addConstrs((at.sum(i, "*") == 1 for i in jobs), name="once")

    # Precedence: a job starts only after each of its predecessors has finished.
    model.addConstrs((start[b] >= start[a] + durations[a] for a, b in links), name="prec")

    # Cumulative resources: at each time s, the jobs running then (job i runs at s when it started
    # at a time t with t <= s < t + durations[i]) need no more of each resource than its capacity.
    # The times s run up to the bound; that range is from the bound, not the statement.
    horizon = range(bound)
    usage = {(r, s): gp.quicksum(needs[i][r] * at[i, t] for i in jobs if needs[i][r] > 0
                                 for t in window[i] if t <= s < t + durations[i])
             for r in resources for s in horizon}
    model.addConstrs((usage[r, s] <= capacities[r] for (r, s) in usage if usage[r, s].size() > 0),
                     name="cap")

    # makespan is the time the last job finishes. Its upper bound is the bound above, not from the statement.
    makespan = model.addVar(lb=0, ub=bound, vtype=GRB.INTEGER, name="makespan")
    model.addConstrs((makespan >= start[i] + durations[i] for i in jobs), name="last")
    # Objective: minimise the makespan.
    model.setObjective(makespan, GRB.MINIMIZE)

    return model, {"start_time": start}


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
