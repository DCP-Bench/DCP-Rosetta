# flowshop_scheduling: a SCIP (Python) model from DCP Rosetta.
# Download the `flowshop_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python flowshop_scheduling.py flowshop_scheduling.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Jobs all go through machines 1 to M in one common order. The first job goes to
    machine 1 while the other jobs wait; when machine 1 has finished it, the job moves on
    to machine 2 and the next job starts on machine 1, and so on. Find the order of the
    jobs that minimises the makespan, the time when the last job leaves the last machine."""
    jobs = instance["jobs"]              # the job ids: their count is the number of jobs n
    machines = instance["machines"]      # the machine ids: their count is the number of machines M
    # process_time[j][m]: the time job row j needs on machine column m, rows in the order of jobs
    process_time = np.array(instance["process_time"])
    # schedules, the listed order, is not read: the model chooses the order itself.

    n = len(jobs)
    M = len(machines)
    # Every completion time is the length of a path of operations, and each operation is
    # on the path at most once, so the sum of all processing times bounds every completion time.
    horizon = int(process_time.sum())

    model = Model("flowshop_scheduling")

    # x[j, p] is 1 when job j is at position p of the order, and 0 when not.
    # A matrix of binaries: the order is a permutation, so each row and each column holds one 1.
    x = model.addMatrixVar((n, n), vtype="B", name="x")
    # C[p, m] is the time the job at position p leaves machine m. Integer, from 0 up to the horizon.
    C = model.addMatrixVar((n, M), vtype="I", lb=0, ub=horizon, name="C")
    # P[p, m] is the processing time of the job at position p on machine m: the time of
    # job j summed over the jobs j placed at p by x.
    P = x.T @ process_time

    # Each position of the order holds exactly one job.
    model.addMatrixCons(x.sum(axis=0) == 1)
    # Each job takes exactly one position in the order.
    model.addMatrixCons(x.sum(axis=1) == 1)

    # Only lower bounds are posted on the completion times. The makespan is minimised, so each
    # completion time is pushed down to the least value that the constraints allow, which is
    # the flowshop recurrence: the later of the two earlier times, plus the job's own time.
    # The first job on the first machine leaves at no earlier than its processing time.
    model.addCons(C[0, 0] >= P[0, 0])
    # A job leaves machine m no earlier than its own time on machine m after it left machine m-1.
    model.addMatrixCons(C[:, 1:] >= C[:, :-1] + P[:, 1:])
    # A machine takes the next position only after it has finished the job in the previous position.
    model.addMatrixCons(C[1:, :] >= C[:-1, :] + P[1:, :])

    # The makespan is the time the last job leaves the last machine; the objective minimises it.
    makespan = C[n - 1, M - 1]
    model.setObjective(makespan, "minimize")

    return model, {"makespan": makespan}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
