# jobshop: a Z3 (Python) model from DCP Rosetta.
# Download the `jobshop.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python jobshop.py jobshop.json

import z3


def create_model(instance):
    """Schedule the tasks of several jobs on machines. The tasks of a job run in order, a
    machine works on one task at a time, and a task runs to completion once started.
    Minimize the makespan, the time when all jobs are finished."""
    jobs_data = instance["jobs_data"]  # jobs_data[j][t] = [machine, duration] of task t of job j

    # The machines the tasks run on.
    machines = sorted({task[0] for job in jobs_data for task in job})

    # Running all the tasks one after another takes this long.
    total_duration = sum(task[1] for job in jobs_data for task in job)

    # start[j][t] is the time task t of job j starts, end[j][t] the time it ends.
    start = [[z3.Int(f"start_{j}_{t}") for t in range(len(job))] for j, job in enumerate(jobs_data)]
    end = [[z3.Int(f"end_{j}_{t}") for t in range(len(job))] for j, job in enumerate(jobs_data)]

    # The time when the last task of all jobs ends.
    makespan = z3.Int("makespan")

    solver = z3.Optimize()

    # Every start and end time lies between 0 and the total duration.
    for j, job in enumerate(jobs_data):
        for t in range(len(job)):
            solver.add(start[j][t] >= 0, start[j][t] <= total_duration)
            solver.add(end[j][t] >= 0, end[j][t] <= total_duration)

    # A task runs for its duration once it starts.
    for j, job in enumerate(jobs_data):
        for t, (_, duration) in enumerate(job):
            solver.add(end[j][t] == start[j][t] + duration)

    # A task starts only after the previous task of its job has ended.
    for j, job in enumerate(jobs_data):
        for t in range(1, len(job)):
            solver.add(start[j][t] >= end[j][t - 1])

    # A machine works on one task at a time: of any two tasks on the same machine,
    # one ends before the other starts.
    for machine in machines:
        tasks = [(j, t) for j, job in enumerate(jobs_data) for t, task in enumerate(job)
                 if task[0] == machine]
        for a in range(len(tasks)):
            for b in range(a + 1, len(tasks)):
                (j1, t1), (j2, t2) = tasks[a], tasks[b]
                solver.add(z3.Or(start[j1][t1] >= end[j2][t2], start[j2][t2] >= end[j1][t1]))

    # The end time of the last task of each job.
    last_ends = [end[j][len(job) - 1] for j, job in enumerate(jobs_data)]

    # The makespan is at least the end of every job, and equals the end of one of them.
    for e in last_ends:
        solver.add(makespan >= e)
    solver.add(z3.Or([makespan == e for e in last_ends]))

    # The makespan is at least the total time of each job, and at least the total time
    # of the tasks on each machine.
    for job in jobs_data:
        solver.add(makespan >= sum(task[1] for task in job))
    for machine in machines:
        solver.add(makespan >= sum(task[1] for job in jobs_data for task in job if task[0] == machine))

    solver.minimize(makespan)

    return solver, {"makespan": makespan}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
