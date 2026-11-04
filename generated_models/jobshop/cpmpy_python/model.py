# jobshop: a CPMpy model from DCP Rosetta.
# Download the `jobshop.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python jobshop.py jobshop.json

import cpmpy as cp


def create_model(instance):
    """Each job is a chain of tasks, and each task needs one machine for a fixed time.
    The tasks of a job run in order, a machine works on one task at a time, and a task
    runs to completion once started. Minimize the makespan, the time the last task ends."""
    jobs_data = instance["jobs_data"]  # jobs_data[j][t] = [machine, duration] of task t of job j

    # Running all tasks one after another takes the sum of all durations, so no
    # optimal schedule needs more time than that.
    horizon = sum(duration for job in jobs_data for _, duration in job)

    # start[j][t] is the time task t of job j starts; it ends duration time units later.
    start = [cp.intvar(0, horizon, shape=len(job), name=f"start_{j}")
             for j, job in enumerate(jobs_data)]
    # The time at which the last task of any job ends.
    makespan = cp.intvar(0, horizon, name="makespan")

    model = cp.Model()

    # A task cannot start before the previous task of its job has ended.
    for j, job in enumerate(jobs_data):
        for t in range(1, len(job)):
            model.add(start[j][t] >= start[j][t - 1] + job[t - 1][1])

    # A machine works on one task at a time: the tasks on one machine never overlap.
    machines = sorted({machine for job in jobs_data for machine, _ in job})
    for machine in machines:
        tasks = [(j, t) for j, job in enumerate(jobs_data)
                 for t, (m, _) in enumerate(job) if m == machine]
        model.add(cp.NoOverlap([start[j][t] for j, t in tasks],
                              [jobs_data[j][t][1] for j, t in tasks]))

    # The makespan is the latest end time. Tasks of a job run in order,
    # so only the last task of each job needs to be looked at.
    model.add(makespan == cp.max([start[j][-1] + job[-1][1] for j, job in enumerate(jobs_data)]))

    # Finish all jobs as early as possible.
    model.minimize(makespan)

    return model, {"makespan": makespan}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
