"""Job-shop scheduling: each job runs its tasks in order, each task needs one machine for a
fixed duration without interruption, a machine runs one task at a time; minimise the makespan.

Interval decisions for the tasks and one list per machine for the order of its tasks.
"""
import json
import sys

import hexaly.optimizer as hx

S = hx.HxSolutionStatus

with open(sys.argv[1]) as f:
    data = json.load(f)
jobs = data["jobs"]  # jobs[j][k] = [machine, duration]
n_machines = 1 + max((m for job in jobs for m, _ in job), default=-1)
horizon = sum(d for job in jobs for _, d in job)

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)
    optimizer.param.time_limit = 90
    model = optimizer.model
    task = [[model.interval(0, horizon) for _ in job] for job in jobs]

    # Each task runs without interruption for its duration, and a job's tasks run in order
    for j, job in enumerate(jobs):
        for k, (_, d) in enumerate(job):
            model.constraint(model.length(task[j][k]) == d)
            if k > 0:
                model.constraint(task[j][k - 1] < task[j][k])  # end <= next start

    # A machine runs at most one task at a time: its tasks follow the order of its list
    for m in range(n_machines):
        on_m = [task[j][k] for j, job in enumerate(jobs) for k, (mm, _) in enumerate(job) if mm == m]
        if len(on_m) < 2:
            continue
        tasks_m = model.array(on_m)
        order = model.list(len(on_m))
        model.constraint(model.count(order) == len(on_m))
        follows = model.lambda_function(lambda i: tasks_m[order[i]] < tasks_m[order[i + 1]])
        model.constraint(model.and_(model.range(0, len(on_m) - 1), follows))

    # The makespan is the time at which the last task finishes
    makespan = model.max(model.end(job[-1]) for job in task if job)
    model.minimize(makespan)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    print("status:", status.name, file=sys.stderr)
    if status in (S.OPTIMAL, S.FEASIBLE):
        start = [[t.value.start() for t in job] for job in task]
        out = {"start": start}
        if status == S.FEASIBLE:
            out["status"] = "feasible"  # best found, not proven optimal
        print(json.dumps(out))
        print("makespan:", makespan.value, "bound:", optimizer.solution.get_objective_bound(0),
              file=sys.stderr)
