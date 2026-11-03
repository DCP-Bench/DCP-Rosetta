# flowshop_scheduling: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `flowshop_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
# Then run it on the first instance (after `pip install ortools`):
#   python flowshop_scheduling.py flowshop_scheduling.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A set of jobs is processed on a series of machines. Every job visits the machines in
    the same order, from machine 1 to machine M, and every machine handles the jobs in one
    common sequence. Find the sequence that minimises the makespan, the time when all jobs
    have been processed."""
    jobs = instance["jobs"]          # the jobs, numbered 1 to n_jobs
    machines = instance["machines"]  # the machines, in the order the jobs visit them
    process_time = instance["process_time"]  # process_time[j][m]: time job j takes on machine m

    n_jobs = len(jobs)
    n_machines = len(machines)

    # Everything run one after the other is a valid schedule, so no job ends later than this.
    horizon = sum(sum(row) for row in process_time)

    model = cp_model.CpModel()

    # sequence[k] is the job in position k of the sequence; every job appears exactly once
    sequence = [model.new_int_var(0, n_jobs - 1, f"sequence_{k}") for k in range(n_jobs)]
    model.add_all_different(sequence)

    # start[k][m] and end[k][m]: when the job in position k starts and ends on machine m
    start = [[model.new_int_var(0, horizon, f"start_{k}_{m}") for m in range(n_machines)]
             for k in range(n_jobs)]
    end = [[model.new_int_var(0, horizon, f"end_{k}_{m}") for m in range(n_machines)]
           for k in range(n_jobs)]

    for m in range(n_machines):
        # the time each job takes on machine m, looked up by the job's number
        times_on_m = [process_time[j][m] for j in range(n_jobs)]
        for k in range(n_jobs):
            # the job in position k takes its processing time on machine m
            duration = model.new_int_var(min(times_on_m), max(times_on_m), f"duration_{k}_{m}")
            model.add_element(sequence[k], times_on_m, duration)
            # the job keeps machine m for its whole processing time
            model.add(end[k][m] == start[k][m] + duration)

    # A job starts on machine m only after it has left machine m-1.
    for k in range(n_jobs):
        for m in range(1, n_machines):
            model.add(start[k][m] >= end[k][m - 1])

    # A machine starts the next job of the sequence only after the previous job has left it.
    for k in range(1, n_jobs):
        for m in range(n_machines):
            model.add(start[k][m] >= end[k - 1][m])

    # makespan: the time the last job leaves the last machine
    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, [end[k][m] for k in range(n_jobs) for m in range(n_machines)])

    # Minimise the makespan.
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
