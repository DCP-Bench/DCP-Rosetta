# jobshop: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `jobshop.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
# Then run it on the first instance (after `pip install ortools`):
#   python jobshop.py jobshop.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Schedule jobs that are chains of tasks, each task on one machine for a fixed time,
    so that the tasks of a job run in order, a machine works on one task at a time, and a
    task runs to completion once started. Minimize the makespan, the time the last task ends."""
    jobs_data = instance["jobs_data"]  # the tasks of each job in order, with machine and duration

    # Running all tasks one after another takes the sum of all durations, so every task ends by then.
    horizon = sum(duration for job in jobs_data for _, duration in job)

    model = cp_model.CpModel()

    # start[j][t]: the time task t of job j starts
    start = [[model.new_int_var(0, horizon, f"start_{j}_{t}") for t in range(len(job))]
             for j, job in enumerate(jobs_data)]
    # end[j][t]: the time task t of job j ends
    end = [[model.new_int_var(0, horizon, f"end_{j}_{t}") for t in range(len(job))]
           for j, job in enumerate(jobs_data)]
    # makespan: the end time of the schedule
    makespan = model.new_int_var(0, horizon, "makespan")

    # A task runs for its duration, from its start to its end.
    intervals_on_machine = {}  # the time intervals of the tasks on each machine
    for j, job in enumerate(jobs_data):
        for t, (machine, duration) in enumerate(job):
            interval = model.new_interval_var(start[j][t], duration, end[j][t], f"task_{j}_{t}")
            intervals_on_machine.setdefault(machine, []).append(interval)

    # A task cannot start before the previous task of its job has ended.
    for j, job in enumerate(jobs_data):
        for t in range(1, len(job)):
            model.add(start[j][t] >= end[j][t - 1])

    # A machine works on one task at a time.
    for intervals in intervals_on_machine.values():
        model.add_no_overlap(intervals)

    # The makespan is the latest end of any task.
    model.add_max_equality(makespan, [e for job_ends in end for e in job_ends])
    model.minimize(makespan)

    return model, {"makespan": makespan}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
