from hermax.model import Model


def greedy_makespan(jobs):
    """Makespan of a feasible schedule built by list scheduling.

    Repeatedly starts the next task of the job that can start earliest. The
    optimum cannot exceed this value, so it bounds every start time.
    """
    job_ready = [0] * len(jobs)
    next_task = [0] * len(jobs)
    machine_free = {}
    end = 0
    remaining = sum(len(job) for job in jobs)
    while remaining:
        best = None
        for j, job in enumerate(jobs):
            if next_task[j] == len(job):
                continue
            machine, _ = job[next_task[j]]
            t = max(job_ready[j], machine_free.get(machine, 0))
            if best is None or t < best[0]:
                best = (t, j)
        t, j = best
        machine, d = jobs[j][next_task[j]]
        machine_free[machine] = t + d
        job_ready[j] = t + d
        next_task[j] += 1
        end = max(end, t + d)
        remaining -= 1
    return end


def build(instance):
    jobs = instance["jobs_data"]
    horizon = greedy_makespan(jobs)

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

    # A machine works on one task at a time: on each machine, the tasks
    # assigned to it form a unit-capacity cumulative resource.
    num_machines = 1 + max(mach for job in jobs for mach, _ in job)
    for mach in range(num_machines):
        starts, durs = [], []
        for j, job in enumerate(jobs):
            for k, (machine, d) in enumerate(job):
                if machine == mach:
                    starts.append(start[j][k])
                    durs.append(d)
        if starts:
            m.cumulative(starts, durs, [1] * len(starts), 1)

    m.obj += makespan
    return m, {"makespan": makespan}
