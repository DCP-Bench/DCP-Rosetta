# flowshop_scheduling: a Choco-solver (Python) model from DCP Rosetta.
# Download the `flowshop_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python flowshop_scheduling.py flowshop_scheduling.json

from pychoco.model import Model


def create_model(instance):
    """A set of jobs is processed on a series of machines. Every job visits the machines in
    the same order, from machine 1 to machine M, and each machine works on one job at a
    time. Find the order of the jobs that minimises the makespan, the time when the last
    job leaves the last machine."""
    jobs = instance["jobs"]          # the jobs, numbered 1 to n_jobs
    schedules = instance["schedules"]  # the job numbers again, 1 to n_jobs
    machines = instance["machines"]  # the machines, numbered 1 to M in the order the jobs visit them
    process_time = instance["process_time"]  # process_time[j][m]: time job j takes on machine m
    n_jobs = len(jobs)
    n_machines = len(machines)

    # Every job run one after another on the machines is a valid schedule, so no job ends later.
    horizon = sum(sum(row) for row in process_time)

    model = Model()

    # sequence[k] is the job in position k of the order
    sequence = [model.intvar(0, n_jobs - 1, name=f"sequence_{k}") for k in range(n_jobs)]
    # Every job appears exactly once in the order.
    model.all_different(sequence).post()

    # duration[k][m] is the time the job in position k takes on machine m
    duration = [[model.intvar(0, max(row[m] for row in process_time), name=f"duration_{k}_{m}")
                 for m in range(n_machines)] for k in range(n_jobs)]
    for k in range(n_jobs):
        for m in range(n_machines):
            model.element(duration[k][m], [process_time[j][m] for j in range(n_jobs)], sequence[k]).post()

    # start[k][m] and end[k][m] are when the job in position k starts and ends on machine m.
    # The first job starts on the first machine at time 0.
    start = [[model.intvar(0, 0 if (k, m) == (0, 0) else horizon, name=f"start_{k}_{m}")
              for m in range(n_machines)] for k in range(n_jobs)]
    end = [[model.intvar(0, horizon, name=f"end_{k}_{m}") for m in range(n_machines)]
           for k in range(n_jobs)]

    for k in range(n_jobs):
        for m in range(n_machines):
            # A job keeps a machine for its whole processing time.
            model.arithm(start[k][m], "+", duration[k][m], "=", end[k][m]).post()
            # A job starts on a machine once it has left the previous machine, and once the job
            # ahead of it in the order has left that machine. Each job starts as early as this allows.
            predecessors = []
            if m > 0:
                predecessors.append(end[k][m - 1])
            if k > 0:
                predecessors.append(end[k - 1][m])
            if len(predecessors) == 1:
                model.arithm(start[k][m], "=", predecessors[0]).post()
            elif len(predecessors) == 2:
                model.max(start[k][m], predecessors).post()

    # The makespan is the time the last job leaves the last machine.
    makespan = model.intvar(0, horizon, name="makespan")
    model.max(makespan, [end[k][m] for k in range(n_jobs) for m in range(n_machines)]).post()

    return model, {"makespan": makespan}, {"objective": makespan, "maximize": False}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
