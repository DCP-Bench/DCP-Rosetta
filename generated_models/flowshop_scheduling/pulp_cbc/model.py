# flowshop_scheduling: a PuLP (Python) model from DCP Rosetta.
# Download the `flowshop_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python flowshop_scheduling.py flowshop_scheduling.json

import pulp


def create_model(instance):
    """A set of jobs is processed on a series of machines. Every job visits the machines in the
    same order, from the first machine to the last, and all machines take the jobs in one common
    sequence. Find the sequence that makes the makespan, the time when the last job leaves the
    last machine, as small as possible."""
    jobs = instance["jobs"]                  # the job numbers
    machines = instance["machines"]          # the machine numbers, in the order every job visits them
    process_time = instance["process_time"]  # process_time[j][m]: the time job j needs on machine m
    n_jobs = len(jobs)                       # the number of jobs
    n_machines = len(machines)               # the number of machines

    # No time in a schedule exceeds the total processing time, since the jobs can run one after another.
    horizon = sum(sum(row) for row in process_time)

    problem = pulp.LpProblem("flowshop", pulp.LpMinimize)

    # position[j][k] is 1 when job j is the k-th job of the sequence, and 0 when not
    position = [[pulp.LpVariable(f"position_{j}_{k}", cat="Binary") for k in range(n_jobs)]
                for j in range(n_jobs)]

    # Every job takes exactly one position in the sequence, and every position holds one job.
    for j in range(n_jobs):
        problem += pulp.lpSum(position[j]) == 1
    for k in range(n_jobs):
        problem += pulp.lpSum(position[j][k] for j in range(n_jobs)) == 1

    # duration[k][m]: the time the job in position k needs on machine m
    duration = [[pulp.lpSum(process_time[j][m] * position[j][k] for j in range(n_jobs))
                 for m in range(n_machines)] for k in range(n_jobs)]

    # start[k][m] and end[k][m]: when the job in position k starts and finishes on machine m
    start = [[pulp.LpVariable(f"start_{k}_{m}", 0, horizon) for m in range(n_machines)]
             for k in range(n_jobs)]
    end = [[pulp.LpVariable(f"end_{k}_{m}", 0, horizon) for m in range(n_machines)]
           for k in range(n_jobs)]

    # The job in position k stays on machine m for its whole processing time.
    for k in range(n_jobs):
        for m in range(n_machines):
            problem += end[k][m] == start[k][m] + duration[k][m]

    # A job starts on a machine only after it has left the machine before it.
    for k in range(n_jobs):
        for m in range(1, n_machines):
            problem += start[k][m] >= end[k][m - 1]

    # A machine starts a job only after it has finished the job before it in the sequence.
    for k in range(1, n_jobs):
        for m in range(n_machines):
            problem += start[k][m] >= end[k - 1][m]

    # makespan: the time the last job leaves the last machine
    makespan = pulp.LpVariable("makespan", 0, horizon, cat="Integer")
    for k in range(n_jobs):
        for m in range(n_machines):
            problem += makespan >= end[k][m]

    # Make the makespan as small as possible.
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
