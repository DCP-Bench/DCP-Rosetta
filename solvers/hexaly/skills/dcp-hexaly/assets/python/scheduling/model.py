"""Job shop: 3 jobs on 3 machines, each job visits the machines in its own order; minimise the makespan.

Shortened from Hexaly's job shop example: interval decisions for the tasks, one list per
machine for the order of its tasks.
"""
import hexaly.optimizer as hx

# JOBS[j] = the tasks of job j in order, as (machine, duration)
JOBS = [[(0, 3), (1, 2), (2, 2)],
        [(0, 2), (2, 1), (1, 4)],
        [(1, 4), (2, 3)]]
MACHINES = 3
HORIZON = sum(d for job in JOBS for _, d in job)

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4  # with 1 or 2 threads the optimum may stay unproven
    optimizer.param.set_gap_limit(0)
    optimizer.param.time_limit = 20
    model = optimizer.model
    task = [[model.interval(0, HORIZON) for _ in job] for job in JOBS]

    # Every task takes its duration, and a job's tasks run in order
    for j, job in enumerate(JOBS):
        for k, (_, d) in enumerate(job):
            model.constraint(model.length(task[j][k]) == d)
            if k > 0:
                model.constraint(task[j][k - 1] < task[j][k])  # end <= next start

    # A machine runs its tasks one after another, in the order its list gives
    for m in range(MACHINES):
        on_m = [task[j][k] for j, job in enumerate(JOBS) for k, (mm, _) in enumerate(job) if mm == m]
        tasks_m = model.array(on_m)
        order = model.list(len(on_m))
        model.constraint(model.count(order) == len(on_m))
        follows = model.lambda_function(lambda i: tasks_m[order[i]] < tasks_m[order[i + 1]])
        model.constraint(model.and_(model.range(0, len(on_m) - 1), follows))

    makespan = model.max(model.end(job[-1]) for job in task)
    model.minimize(makespan)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    print("Status:", status.name)
    if status in (hx.HxSolutionStatus.FEASIBLE, hx.HxSolutionStatus.OPTIMAL):
        print("Makespan:", makespan.value)
        for j, job in enumerate(task):
            print(f"job {j} starts:", [t.value.start() for t in job])
