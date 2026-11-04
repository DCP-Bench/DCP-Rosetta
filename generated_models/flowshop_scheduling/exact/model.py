# flowshop_scheduling: an Exact (Python) model from DCP Rosetta.
# Download the `flowshop_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python flowshop_scheduling.py flowshop_scheduling.json

from exact import Exact


def create_model(instance):
    """A set of jobs is processed on a series of machines in the same order, from the first machine
    to the last, and each machine works on one job at a time. Find the job order that minimises the
    makespan, the time when the last job leaves the last machine."""
    n_jobs = len(instance["jobs"])  # the number of jobs
    n_machines = len(instance["machines"])  # the number of machines
    p = instance["process_time"]  # p[j][m]: the time job j takes on machine m
    jobs = range(n_jobs)  # the job numbers
    machines = range(n_machines)  # the machine numbers, in the order the jobs visit them

    # finish[m]: when machine m finishes, with the jobs taken in the listed order. The best order
    # finishes no later, so the last value bounds every start time.
    finish = [0] * n_machines
    for j in jobs:
        for m in machines:
            finish[m] = max(finish[m], finish[m - 1] if m > 0 else 0) + p[j][m]
    horizon = finish[-1]

    solver = Exact()

    # Exact identifies its variables by name.
    # before[i, j] is 1 when job i is processed before job j, and 0 when job j comes first (i < j)
    before = {}
    for i in jobs:
        for j in range(i + 1, n_jobs):
            before[i, j] = f"job_{i}_before_{j}"
            solver.addVariable(before[i, j], 0, 1)

    # Terms and a constant whose sum is 1 exactly when job a is processed before job b.
    def precedes(a, b):
        if a < b:
            return [(1, before[a, b])], 0
        return [(-1, before[b, a])], 1

    # No three jobs form a cycle: if i comes before j and j before k, then i comes before k.
    for i in jobs:
        for j in range(i + 1, n_jobs):
            for k in range(j + 1, n_jobs):
                solver.addConstraint([(1, before[i, j]), (1, before[j, k]), (-1, before[i, k])],
                                     True, 0, True, 1)

    # start[j][m] is the time job j starts on machine m
    start = [[f"start_{j}_{m}" for m in machines] for j in jobs]
    for j in jobs:
        for m in machines:
            solver.addVariable(start[j][m], 0, horizon)

    # A job starts on a machine only after it has finished on the machine before.
    for j in jobs:
        for m in range(1, n_machines):
            solver.addConstraint([(1, start[j][m]), (-1, start[j][m - 1])], True, p[j][m - 1])

    # Two jobs on the same machine do not overlap: the one that comes first finishes there before
    # the other starts. The horizon is large enough to switch off the inequality that does not apply.
    for i in jobs:
        for j in range(i + 1, n_jobs):
            for m in machines:
                # If job i comes first, job j starts on machine m after job i has finished there.
                solver.addConstraint([(1, start[j][m]), (-1, start[i][m]), (-horizon, before[i, j])],
                                     True, p[i][m] - horizon)
                # Otherwise job i starts on machine m after job j has finished there.
                solver.addConstraint([(1, start[i][m]), (-1, start[j][m]), (horizon, before[i, j])],
                                     True, p[j][m])

    # makespan is the time the last job leaves the last machine.
    solver.addVariable("makespan", 0, horizon)
    for j in jobs:
        solver.addConstraint([(1, "makespan"), (-1, start[j][-1])], True, p[j][-1])

    # tail_min[m] is the least time any job still needs after machine m, and head_min[m] the least
    # time any job needs before it reaches machine m.
    tail_min = [min(sum(p[j][m + 1:]) for j in jobs) for m in machines]
    head_min = [min(sum(p[j][:m]) for j in jobs) for m in machines]
    for m in machines:
        for j in jobs:
            # Job j starts on machine m after the head time and after the jobs ahead of it there.
            terms = [(1, start[j][m])]  # start of job j, minus the work of each job ahead of it
            rhs = head_min[m]  # the head time, plus the work of each job ahead of it
            for i in jobs:
                if i != j and p[i][m]:
                    order_terms, order_const = precedes(i, j)
                    terms += [(-p[i][m] * coef, name) for coef, name in order_terms]
                    rhs += p[i][m] * order_const
            solver.addConstraint(terms, True, rhs)
            # The makespan is at least the end of job j on machine m, plus the work of the jobs after
            # it there, plus the tail time after machine m.
            terms = [(1, "makespan"), (-1, start[j][m])]  # makespan, minus the start of job j
            rhs = p[j][m] + tail_min[m]  # the time of job j on machine m, plus the tail time
            for i in jobs:
                if i != j and p[i][m]:
                    order_terms, order_const = precedes(j, i)
                    terms += [(-p[i][m] * coef, name) for coef, name in order_terms]
                    rhs += p[i][m] * order_const
            solver.addConstraint(terms, True, rhs)

    # The smallest makespan.
    solver.setObjective([(1, "makespan")], minimize=True)

    return solver, {"makespan": "makespan"}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
