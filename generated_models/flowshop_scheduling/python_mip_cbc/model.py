# flowshop_scheduling: a Python-MIP (Python) model from DCP Rosetta.
# Download the `flowshop_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python flowshop_scheduling.py flowshop_scheduling.json

import mip


def create_model(instance):
    """A set of jobs is processed on a series of machines. Every job visits the machines in the
    same order, from the first machine to the last, and every machine handles the jobs in one
    common order. Find the order of the jobs that minimises the makespan, the time when the
    last job leaves the last machine."""
    jobs = instance["jobs"]                  # the jobs
    machines = instance["machines"]          # the machines, in the order every job visits them
    process_time = instance["process_time"]  # process_time[j][m]: the time job j takes on machine m

    n_jobs = len(jobs)
    n_machines = len(machines)

    # The total processing time of all jobs on all machines. Running the jobs one after another takes
    # this long, so no completion time is later than it.
    total = sum(sum(row) for row in process_time)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[j][p] is 1 when job j is in position p of the order, and 0 when not.
    x = [[model.add_var(f"x_{j}_{p}", var_type=mip.BINARY) for p in range(n_jobs)] for j in range(n_jobs)]

    # Each job takes exactly one position in the order.
    for j in range(n_jobs):
        model += mip.xsum(x[j][p] for p in range(n_jobs)) == 1

    # Each position is taken by exactly one job.
    for p in range(n_jobs):
        model += mip.xsum(x[j][p] for j in range(n_jobs)) == 1

    # c[p][m] is the time when the job in position p leaves machine m.
    c = [
        [model.add_var(f"c_{p}_{m}", lb=0, ub=total, var_type=mip.INTEGER) for m in range(n_machines)]
        for p in range(n_jobs)
    ]
    for p in range(n_jobs):
        for m in range(n_machines):
            # The time the job in position p needs on machine m.
            proc = mip.xsum(process_time[j][m] * x[j][p] for j in range(n_jobs))
            # The job in position p leaves the first machine after its processing time.
            if p == 0 and m == 0:
                model += c[0][0] >= proc
            # A machine works on one job at a time, so the job in position p leaves machine m
            # after the job in position p - 1 has left it.
            if p > 0:
                model += c[p][m] >= c[p - 1][m] + proc
            # A job moves on in series, so it leaves machine m after it has left machine m - 1.
            if m > 0:
                model += c[p][m] >= c[p][m - 1] + proc

    # makespan is the time when the last job leaves the last machine.
    makespan = model.add_var("makespan", lb=0, ub=total, var_type=mip.INTEGER)
    model += makespan == c[n_jobs - 1][n_machines - 1]

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
