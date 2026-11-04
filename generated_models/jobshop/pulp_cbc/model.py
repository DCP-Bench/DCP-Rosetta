# jobshop: a PuLP (Python) model from DCP Rosetta.
# Download the `jobshop.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python jobshop.py jobshop.json

import itertools

import pulp


def create_model(instance):
    """Several jobs are processed on several machines. Each job is a sequence of tasks that
    run in the given order, each on its own machine for a fixed time. A machine does one
    task at a time, and a task runs without interruption. Find the shortest schedule: the
    time at which the last task ends."""
    jobs_data = instance["jobs_data"]  # jobs_data[j][t]: the machine and duration of task t of job j

    # Running all tasks one after another takes this long, so every task ends by then.
    horizon = sum(duration for job in jobs_data for _, duration in job)

    problem = pulp.LpProblem("jobshop", pulp.LpMinimize)

    # start[j][t] is the time at which task t of job j starts.
    start = [[pulp.LpVariable(f"start_{j}_{t}", 0, horizon) for t in range(len(job))]
             for j, job in enumerate(jobs_data)]

    # makespan is the time at which the last task ends.
    makespan = pulp.LpVariable("makespan", 0, horizon, cat="Integer")

    # The tasks of a job run in order: each starts after the previous one ends. The makespan
    # is no earlier than the end of the last task of the job.
    for j, job in enumerate(jobs_data):
        for t in range(1, len(job)):
            problem += start[j][t] >= start[j][t - 1] + job[t - 1][1]
        problem += makespan >= start[j][-1] + job[-1][1]

    # tasks_on[machine] lists the (job, task, duration) of every task on that machine.
    tasks_on = {}
    for j, job in enumerate(jobs_data):
        for t, (machine, duration) in enumerate(job):
            tasks_on.setdefault(machine, []).append((j, t, duration))

    # Tasks on the same machine do not overlap. before is 1 when the first task of the pair
    # runs before the second, and 0 when the second runs first.
    for tasks in tasks_on.values():
        for (j1, t1, d1), (j2, t2, d2) in itertools.combinations(tasks, 2):
            before = pulp.LpVariable(f"before_{j1}_{t1}_{j2}_{t2}", cat="Binary")
            problem += start[j1][t1] + d1 <= start[j2][t2] + horizon * (1 - before)
            problem += start[j2][t2] + d2 <= start[j1][t1] + horizon * before

    # Finish all jobs as early as possible.
    problem += makespan

    return problem, {"makespan": makespan}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
