# jobshop: a PyCSP3 model from DCP Rosetta.
# Download the `jobshop.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python jobshop.py jobshop.json

from pycsp3 import *


def create_model(instance):
    """In a job shop, several jobs are processed on several machines. Each job is a sequence of tasks
    that must be performed in the given order, each task on a specific machine. A machine works on one
    task at a time, and a task once started runs to completion. Schedule the tasks so as to minimise the
    makespan, the time it takes for all the jobs to be completed."""
    jobs_data = instance["jobs_data"]  # jobs_data[j][k] is [machine, duration] of task k of job j; machines are 0-based
    durations = [[duration for _, duration in job] for job in jobs_data]  # durations[j][k]: how long task k of job j takes
    machines = sorted({machine for job in jobs_data for machine, _ in job})  # the machines the tasks run on, in increasing order

    # horizon is the sum of all durations, taken as the bound on every start time: running the tasks one after
    # another is a schedule of that length, so an optimal schedule never ends later than horizon
    horizon = sum(sum(job) for job in durations)

    # tasks_on[m] lists the (job, task) pairs that run on machine m
    tasks_on = {m: [(j, k) for j, job in enumerate(jobs_data) for k, (machine, _) in enumerate(job) if machine == m] for m in machines}

    # start[j][k] is the start time of task k of job j; each job's VarArray needs its own id, since a VarArray
    # created in a comprehension otherwise gets a duplicate identifier
    start = [VarArray(size=len(job), dom=range(horizon), id=f"start{j}") for j, job in enumerate(jobs_data)]

    # makespan is the time at which the last job completes
    makespan = Var(dom=range(horizon + 1))

    satisfy(
        # No task of a job starts before the previous task of that job has finished.
        [start[j][k + 1] >= start[j][k] + durations[j][k] for j, job in enumerate(jobs_data) for k in range(len(job) - 1)],
        # A machine works on one task at a time: the tasks on each machine do not overlap.
        [NoOverlap(origins=[start[j][k] for j, k in tasks_on[m]], lengths=[durations[j][k] for j, k in tasks_on[m]]) for m in machines],
        # The makespan is at least the time each job's last task finishes.
        [makespan >= start[j][-1] + durations[j][-1] for j in range(len(jobs_data))],
    )

    # The objective is the makespan, to be minimised.
    minimize(makespan)

    return {"makespan": makespan}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
