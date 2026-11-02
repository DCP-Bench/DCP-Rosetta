"""Job-shop scheduling: each job's tasks run in order, each on its own machine for a fixed
duration without interruption; a machine runs one task at a time. Minimise the makespan.

An interval decision per task and one list decision per machine for the order of its tasks.
"""
import json
import sys

import hexaly.optimizer as hx

S = hx.HxSolutionStatus

with open(sys.argv[1]) as f:
    jobs = json.load(f)["jobs"]  # jobs[j][k] = [machine, duration] of task k of job j
machines = 1 + max((m for job in jobs for m, _ in job), default=-1)
horizon = sum(d for job in jobs for _, d in job)

with hx.HexalyOptimizer() as optimizer:
    param = optimizer.param
    param.verbosity = 0
    param.nb_threads = 4  # the bound that proves the optimum runs beside the search
    param.set_gap_limit(0)  # OPTIMAL must mean proven exactly
    param.time_limit = 90
    model = optimizer.model
    task = [[model.interval(0, horizon) for _ in job] for job in jobs]

    # Every task runs for its duration without interruption, and a job's tasks run in order
    for j, job in enumerate(jobs):
        for k, (_, d) in enumerate(job):
            model.constraint(model.length(task[j][k]) == d)
            if k > 0:
                model.constraint(task[j][k - 1] < task[j][k])  # end <= next start

    # A machine runs at most one task at a time: its tasks follow the order of its list
    for m in range(machines):
        on_m = [task[j][k] for j, job in enumerate(jobs) for k, (mm, _) in enumerate(job) if mm == m]
        if len(on_m) < 2:
            continue
        tasks_m = model.array(on_m)
        order = model.list(len(on_m))
        model.constraint(model.count(order) == len(on_m))
        follows = model.lambda_function(lambda i: tasks_m[order[i]] < tasks_m[order[i + 1]])
        model.constraint(model.and_(model.range(0, len(on_m) - 1), follows))

    # The makespan, the end of the last task, is as small as possible
    makespan = model.max(model.end(job[-1]) for job in task if job)
    model.minimize(makespan)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    if status in (S.OPTIMAL, S.FEASIBLE):
        if status != S.OPTIMAL:
            print("warning: best found, optimality not proven", file=sys.stderr)
        print(json.dumps({"start": [[t.value.start() for t in job] for job in task]}))
        print(f"status {status.name} makespan {makespan.value} bound {optimizer.solution.get_objective_bound(0)}",
              file=sys.stderr)
    else:
        print(f"no schedule found: {status.name}", file=sys.stderr)
