# jobshop: a Python-MIP (Python) model from DCP Rosetta.
# Download the `jobshop.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python jobshop.py jobshop.json

import mip


def create_model(instance):
    """Schedule the tasks of several jobs on machines so that all jobs are finished as early
    as possible. The tasks of a job run in a fixed order, each task runs on one machine
    without stopping, and a machine works on one task at a time."""
    jobs_data = instance["jobs_data"]  # jobs_data[j][t]: [machine, duration] of task t of job j

    # horizon: the total duration of all tasks. Running them one after another takes this
    # long, so no task ends later.
    horizon = sum(duration for job in jobs_data for _, duration in job)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # start[j][t] is the time task t of job j starts. The task ends after its duration.
    start = [
        [
            model.add_var(f"s_{j}_{t}", lb=0, ub=horizon - duration, var_type=mip.INTEGER)
            for t, (_, duration) in enumerate(job)
        ]
        for j, job in enumerate(jobs_data)
    ]

    # makespan: the time the last task of all jobs ends.
    makespan = model.add_var("makespan", lb=0, ub=horizon, var_type=mip.INTEGER)

    # A task starts only after the previous task of its job has ended.
    for j, job in enumerate(jobs_data):
        for t in range(len(job) - 1):
            model.add_constr(start[j][t + 1] >= start[j][t] + job[t][1])

    # The makespan is at least the end of the last task of each job. A job with no tasks does not count.
    for j, job in enumerate(jobs_data):
        if job:
            last = len(job) - 1
            model.add_constr(makespan >= start[j][last] + job[last][1])

    # tasks_on[machine]: the (job, task, duration) of each task that runs on that machine.
    tasks_on = {}
    for j, job in enumerate(jobs_data):
        for t, (machine, duration) in enumerate(job):
            tasks_on.setdefault(machine, []).append((j, t, duration))

    # Two tasks on the same machine do not overlap, so one of them runs before the other.
    for machine in sorted(tasks_on):
        tasks = tasks_on[machine]
        for a in range(len(tasks)):
            for b in range(a + 1, len(tasks)):
                ja, ta, da = tasks[a]
                jb, tb, db = tasks[b]
                if ja == jb:
                    # Tasks of the same job are already in order.
                    continue
                # before is 1 when task ta of job ja runs before task tb of job jb, and 0 when it runs after.
                before = model.add_var(f"before_{ja}_{ta}_{jb}_{tb}", var_type=mip.BINARY)
                model.add_constr(start[jb][tb] >= start[ja][ta] + da - horizon * (1 - before))
                model.add_constr(start[ja][ta] >= start[jb][tb] + db - horizon * before)

    # Finish all jobs as early as possible.
    model.objective = makespan

    return model, {"makespan": makespan}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
