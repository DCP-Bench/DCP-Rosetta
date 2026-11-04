# flowshop_scheduling: a Z3 (Python) model from DCP Rosetta.
# Download the `flowshop_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python flowshop_scheduling.py flowshop_scheduling.json

import z3


def create_model(instance):
    """A set of jobs is processed on a series of machines. Every job visits the machines in the
    same order, from machine 1 to the last machine, and every machine handles the jobs in one
    common order. Find the order of the jobs that minimises the makespan, the time when the last
    job leaves the last machine."""
    process_time = instance["process_time"]  # process_time[j][m]: time job j takes on machine m
    n_jobs = len(process_time)               # number of jobs
    n_machines = len(process_time[0])        # number of machines

    # Running all the work one job after the other is a valid schedule, so no time goes beyond this.
    max_duration = sum(sum(row) for row in process_time)

    # before[(i, j)] is true when job i comes before job j in the common order, for i < j.
    before = {(i, j): z3.Bool(f"before_{i}_{j}")
              for i in range(n_jobs) for j in range(i + 1, n_jobs)}

    def comes_before(i, j):
        # True when job i comes before job j, for any two different jobs.
        return before[(i, j)] if i < j else z3.Not(before[(j, i)])

    # start[j][m] is the time job j starts on machine m
    start = [[z3.Int(f"start_{j}_{m}") for m in range(n_machines)] for j in range(n_jobs)]

    # makespan is the time the last job leaves the last machine
    makespan = z3.Int("makespan")

    solver = z3.Optimize()

    # The common order is a sequence: if job i comes before job j and job j before job k, then
    # job i comes before job k.
    for i in range(n_jobs):
        for j in range(n_jobs):
            for k in range(n_jobs):
                if len({i, j, k}) == 3:
                    solver.add(z3.Implies(z3.And(comes_before(i, j), comes_before(j, k)),
                                          comes_before(i, k)))

    # Every job starts at time 0 or later and finishes within the total work.
    for j in range(n_jobs):
        for m in range(n_machines):
            solver.add(start[j][m] >= 0)
            solver.add(start[j][m] + process_time[j][m] <= max_duration)

    # A job starts on a machine only after it has finished on the machine before.
    for j in range(n_jobs):
        for m in range(1, n_machines):
            solver.add(start[j][m] >= start[j][m - 1] + process_time[j][m - 1])

    # A machine handles one job at a time, in the common order: the later job starts on every
    # machine only after the earlier one has finished there.
    for i in range(n_jobs):
        for j in range(i + 1, n_jobs):
            for m in range(n_machines):
                solver.add(z3.If(before[(i, j)],
                                 start[j][m] >= start[i][m] + process_time[i][m],
                                 start[i][m] >= start[j][m] + process_time[j][m]))

    # The makespan is the latest time a job leaves the last machine.
    last = n_machines - 1
    # ends[j] is the time job j leaves the last machine
    ends = [start[j][last] + process_time[j][last] for j in range(n_jobs)]
    solver.add([makespan >= e for e in ends])
    solver.add(z3.Or([makespan == e for e in ends]))

    # A lower bound on the makespan, for each machine.
    for m in range(n_machines):
        # head is the shortest time a job spends on the machines before m
        head = min(sum(process_time[j][:m]) for j in range(n_jobs))
        # tail is the shortest time a job spends on the machines after m
        tail = min(sum(process_time[j][m + 1:]) for j in range(n_jobs))
        # Machine m must process every job, and a job cannot reach it before its head time
        # or leave it before its tail time.
        solver.add(makespan >= head + sum(process_time[j][m] for j in range(n_jobs)) + tail)

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
