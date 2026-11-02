"""Job-shop scheduling: each job is a sequence of tasks run in the given order, each task needs one
machine for a fixed duration without interruption, and a machine runs one task at a time.
Minimise the makespan, the time the last task finishes; time starts at 0.

Interval decisions for the tasks and one list decision per machine for the order of its tasks.
Prints one optimal schedule as {"start": [[...], ...]}.
"""
import json
import sys
import time

import hexaly.optimizer as hx

S = hx.HxSolutionStatus

with open(sys.argv[1]) as f:
    jobs = json.load(f)["jobs"]  # jobs[j][k] = [machine, duration]
machines = 1 + max((m for job in jobs for m, _ in job), default=-1)
horizon = sum(d for job in jobs for _, d in job)

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4  # with 1 or 2 threads the optimum may stay unproven
    optimizer.param.set_gap_limit(0)  # OPTIMAL must mean proven exactly
    optimizer.param.time_limit = 90
    model = optimizer.model
    task = [[model.interval(0, horizon) for _ in job] for job in jobs]

    # Each task runs for its duration without interruption, and a job's tasks run in order
    for j, job in enumerate(jobs):
        for k, (_, d) in enumerate(job):
            model.constraint(model.length(task[j][k]) == d)
            if k > 0:
                model.constraint(task[j][k - 1] < task[j][k])  # end of the previous <= start of the next

    # A machine runs at most one task at a time: its tasks follow one another in the order of its list
    for m in range(machines):
        on_m = [task[j][k] for j, job in enumerate(jobs) for k, (mm, _) in enumerate(job) if mm == m]
        if len(on_m) < 2:
            continue
        tasks_m = model.array(on_m)
        order = model.list(len(on_m))
        model.constraint(model.count(order) == len(on_m))
        follows = model.lambda_function(lambda i: tasks_m[order[i]] < tasks_m[order[i + 1]])
        model.constraint(model.and_(model.range(0, len(on_m) - 1), follows))

    # The makespan is the time the last task finishes
    makespan = model.max(model.end(job[-1]) for job in task if job)
    model.minimize(makespan)
    model.close()
    started = time.monotonic()
    optimizer.solve()

    status = optimizer.solution.status
    value = makespan.value if status in (S.OPTIMAL, S.FEASIBLE) else None
    print(f"status {status.name} makespan {value} bound {optimizer.solution.get_objective_bound(0)} "
          f"solve {time.monotonic() - started:.2f} s", file=sys.stderr)
    if status in (S.OPTIMAL, S.FEASIBLE):
        if status != S.OPTIMAL:
            print("warning: optimality not proven", file=sys.stderr)
        print(json.dumps({"start": [[t.value.start() for t in job] for job in task]}))
    elif status == S.INCONSISTENT:
        print(json.dumps({"status": "unsatisfiable"}))
    else:
        print("no schedule found within the time limit", file=sys.stderr)
        sys.exit(1)
