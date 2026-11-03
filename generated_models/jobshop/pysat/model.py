# jobshop: a PySAT (Python) model from DCP Rosetta.
# Download the `jobshop.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python jobshop.py jobshop.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer


def create_model(instance):
    """Schedule the tasks of several jobs on their machines so that the last task ends as
    early as possible. The tasks of a job run in their given order, a machine works on one
    task at a time, and a task, once started, runs to completion."""
    jobs = instance["jobs_data"]  # jobs[j][k] = [machine, duration] of task k of job j

    pool = IDPool()
    formula = WCNF()

    def starts_at_or_after(x, v):
        # The comparison "x >= v", which is fixed when v lies outside the range of x.
        if v <= x.lb:
            return True
        if v > x.ub:
            return False
        return x.ge(v)

    def require(lits):
        # At least one of these comparisons holds. A comparison that is always true
        # satisfies the requirement; one that is always false is left out.
        if any(lit is True for lit in lits):
            return
        formula.append([lit for lit in lits if lit is not False])

    def negate(lit):
        return (not lit) if isinstance(lit, bool) else -lit

    # Upper bound on the makespan: the end of a schedule built greedily, where each step
    # starts the next task of the job that can start earliest.
    job_free = [0] * len(jobs)                 # job_free[j]: the time job j's last scheduled task ends
    machine_free = {}                          # machine_free[m]: the time machine m's last scheduled task ends
    next_task = [0] * len(jobs)                # next_task[j]: the index of the next unscheduled task of job j
    remaining = sum(len(job) for job in jobs)  # the number of unscheduled tasks
    horizon = 0                                # the end of the latest scheduled task
    while remaining:
        best = None  # the earliest start among the next tasks, and its job
        for j, job in enumerate(jobs):
            if next_task[j] < len(job):
                m, d = job[next_task[j]]
                earliest = max(job_free[j], machine_free.get(m, 0))
                if best is None or earliest < best[0]:
                    best = (earliest, j)
        earliest, j = best
        m, d = jobs[j][next_task[j]]
        job_free[j] = machine_free[m] = earliest + d
        horizon = max(horizon, earliest + d)
        next_task[j] += 1
        remaining -= 1

    # Lower bound on the makespan: no schedule is shorter than its longest job, or than the
    # total work on its busiest machine. It stays at or below the greedy bound.
    load = {}  # load[m]: the total duration of the tasks on machine m
    for job in jobs:
        for m, d in job:
            load[m] = load.get(m, 0) + d
    lower = max([sum(d for _, d in job) for job in jobs] + list(load.values()) + [0])
    lower = min(lower, horizon)

    # start[j][k]: the start time of task k of job j. A task cannot start before the tasks
    # before it in the job are done, and it must leave time for the tasks after it.
    start = []
    for j, job in enumerate(jobs):
        row = []
        head = 0                        # the time the earlier tasks of the job take
        tail = sum(d for _, d in job)   # the time task k and the tasks after it take
        for k, (m, d) in enumerate(job):
            row.append(Integer(f"start_{j}_{k}", head, max(horizon - tail, head),
                               encoding="order", vpool=pool))
            head += d
            tail -= d
        start.append(row)

    # Each start time is one whole number in its range.
    for row in start:
        for x in row:
            formula.extend(x.domain_clauses())

    # Task k+1 of a job starts after task k of that job ends.
    for j, job in enumerate(jobs):
        for k in range(len(job) - 1):
            a, b, d = start[j][k], start[j][k + 1], job[k][1]
            for t in range(a.lb, a.ub + 1):
                require([negate(starts_at_or_after(a, t)), starts_at_or_after(b, t + d)])

    # A machine works on one task at a time: of two tasks on the same machine, one ends
    # before the other starts. a_first is true when task a of the pair runs first.
    tasks = [(j, k) for j, job in enumerate(jobs) for k in range(len(job))]
    for x in range(len(tasks)):
        for y in range(x + 1, len(tasks)):
            (j1, k1), (j2, k2) = tasks[x], tasks[y]
            if j1 == j2 or jobs[j1][k1][0] != jobs[j2][k2][0]:
                continue
            a, da = start[j1][k1], jobs[j1][k1][1]
            b, db = start[j2][k2], jobs[j2][k2][1]
            a_first = pool.id(("a_first", j1, k1, j2, k2))
            for t in range(a.lb, a.ub + 1):
                require([-a_first, negate(starts_at_or_after(a, t)), starts_at_or_after(b, t + da)])
            for t in range(b.lb, b.ub + 1):
                require([a_first, negate(starts_at_or_after(b, t)), starts_at_or_after(a, t + db)])

    # makespan: the time the last task of the schedule ends. It lies from the lower bound up
    # to the greedy bound, and at least one above the lower bound so that its range is not empty.
    makespan = Integer("makespan", lower, max(horizon, lower + 1),
                       encoding="coupled", vpool=pool)
    formula.extend(makespan.domain_clauses())

    # The makespan is at least the end of the last task of every job.
    for j, job in enumerate(jobs):
        if not job:
            continue
        last, d = start[j][-1], job[-1][1]
        for t in range(last.lb, last.ub + 1):
            require([negate(starts_at_or_after(last, t)), starts_at_or_after(makespan, t + d)])

    # The makespan stays within the greedy bound.
    if horizon < makespan.ub:
        require([negate(starts_at_or_after(makespan, horizon + 1))])

    # Minimise the makespan: each time unit it lies above its lower bound costs 1.
    for v in range(makespan.lb + 1, makespan.ub + 1):
        formula.append([-makespan.ge(v)], weight=1)

    return formula, {"makespan": makespan}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
