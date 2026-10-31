from hermax.model import Model


def build(instance):
    jobs = instance["jobs_data"]
    horizon = sum(d for job in jobs for _, d in job)

    m = Model()
    # start[j][k] is the start time of task k of job j.
    start = [
        [m.int(f"s_{j}_{k}", 0, horizon) for k in range(len(job))]
        for j, job in enumerate(jobs)
    ]
    makespan = m.int("makespan", 0, horizon)

    # No task starts before the previous task of its job has completed.
    for j, job in enumerate(jobs):
        for k in range(len(job) - 1):
            m &= (start[j][k] + job[k][1] <= start[j][k + 1])
        m &= (start[j][len(job) - 1] + job[-1][1] <= makespan)

    # A machine works on one task at a time: for every pair of tasks on the
    # same machine, one must finish before the other starts.
    tasks = [
        (j, k, machine, d)
        for j, job in enumerate(jobs)
        for k, (machine, d) in enumerate(job)
    ]
    for i, (j1, k1, mach1, d1) in enumerate(tasks):
        for j2, k2, mach2, d2 in tasks[i + 1:]:
            if mach1 != mach2:
                continue
            before = m.bool()
            after = m.bool()
            m &= (start[j1][k1] + d1 <= start[j2][k2]).iff(before)
            m &= (start[j2][k2] + d2 <= start[j1][k1]).iff(after)
            m &= (before | after)

    m.obj += makespan
    return m, {"makespan": makespan}
