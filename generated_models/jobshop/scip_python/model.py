# jobshop: a SCIP (Python) model from DCP Rosetta.
# Download the `jobshop.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python jobshop.py jobshop.json

from pyscipopt import Model


def create_model(instance):
    """Job shop scheduling. Each job is a sequence of tasks that must run in
    order, and each task runs for a fixed time on one given machine. A machine
    works on one task at a time, and a task, once started, runs to completion.
    Schedule all jobs so that the makespan, the time at which the last task
    finishes, is as small as possible."""
    # jobs[j][k] = [machine, duration] of task k of job j; machines are numbered from 0
    jobs = instance["jobs_data"]

    model = Model("jobshop")

    # Running every task one after another, back to back, takes the sum of all
    # durations, so the optimal makespan is at most this horizon. It is computed
    # from the instance's durations and bounds the makespan and every start time.
    horizon = sum(duration for job in jobs for _, duration in job)

    # start[j][k] is the time at which task k of job j starts. Times are integers
    # because the durations are: a left-justified schedule starts each task at a
    # sum of durations. Jobs can have different numbers of tasks, so the starts are
    # nested lists, not a matrix. A task finishes by the makespan, which is at most
    # the horizon, so it starts no later than horizon minus its duration.
    start = [
        [
            model.addVar(f"start_{j}_{k}", vtype="I", lb=0, ub=horizon - duration)
            for k, (_, duration) in enumerate(job)
        ]
        for j, job in enumerate(jobs)
    ]

    # makespan is the time at which the last task finishes, the objective. The
    # horizon bounds it, since the optimal makespan is at most the horizon.
    makespan = model.addVar("makespan", vtype="I", lb=0, ub=horizon)

    # The tasks of a job run in their order: each task starts only after the
    # previous task of the same job has finished.
    for j, job in enumerate(jobs):
        for k in range(len(job) - 1):
            model.addCons(start[j][k] + job[k][1] <= start[j][k + 1])

    # A machine works on one task at a time. SCIP has no no-overlap constraint, so
    # for each machine its tasks form a cumulative constraint: every task needs 1
    # unit of a resource with capacity 1, so no two of them run at the same time.
    machines = sorted({task_machine for job in jobs for task_machine, _ in job})
    for machine in machines:
        on_machine = [
            (start[j][k], duration)
            for j, job in enumerate(jobs)
            for k, (task_machine, duration) in enumerate(job)
            if task_machine == machine
        ]
        model.addConsCumulative(
            [s for s, _ in on_machine],
            [d for _, d in on_machine],
            [1] * len(on_machine),
            1,
        )

    # The makespan is at least the finish time of the last task of every job. With
    # the order constraints above, that is the latest finish of any task.
    for j, job in enumerate(jobs):
        last = len(job) - 1
        model.addCons(makespan >= start[j][last] + job[last][1])

    # Objective: minimise the makespan.
    model.setObjective(makespan, "minimize")

    return model, {"makespan": makespan}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
