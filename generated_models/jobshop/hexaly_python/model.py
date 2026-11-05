"""Job shop: schedule each job's tasks in order on their machines, one task per machine at a time, minimising the makespan."""
import hexaly.optimizer as hx


def build(instance):
    jobs = instance["jobs_data"]  # jobs[j] = [[machine, duration], ...] in processing order
    horizon = sum(d for job in jobs for _, d in job)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # start[j][k] is the start time of task k of job j. Integer starts with pairwise
    # disjunctions give Hexaly bounds it can close.
    start = [[model.int(0, horizon) for _ in job] for job in jobs]

    # The tasks of a job run in order, each to completion
    for j, job in enumerate(jobs):
        for k in range(1, len(job)):
            model.constraint(start[j][k - 1] + job[k - 1][1] <= start[j][k])
    # A machine runs one task at a time: of two tasks on it, one ends before the other starts
    tasks = [(j, k) for j, job in enumerate(jobs) for k in range(len(job))]
    for a in range(len(tasks)):
        for b in range(a + 1, len(tasks)):
            (j1, k1), (j2, k2) = tasks[a], tasks[b]
            if j1 != j2 and jobs[j1][k1][0] == jobs[j2][k2][0]:
                model.constraint(model.or_(start[j1][k1] + jobs[j1][k1][1] <= start[j2][k2],
                                           start[j2][k2] + jobs[j2][k2][1] <= start[j1][k1]))

    # Minimise the makespan, when the last task finishes
    makespan = model.max(start[j][-1] + job[-1][1] for j, job in enumerate(jobs))
    model.minimize(makespan)
    return optimizer, {"makespan": makespan}
