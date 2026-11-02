# jobshop: an Exact (Python) model from DCP Rosetta.
# Download the `jobshop.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python jobshop.py jobshop.json

from exact import Exact


def create_model(instance):
    """Schedule the tasks of several jobs on machines, so that the tasks of each job run in
    order, each machine runs one task at a time, and a task runs to completion once started.
    Minimise the makespan, the time at which the last task finishes."""
    jobs_data = instance["jobs_data"]  # the tasks of each job in order, each with its machine and duration

    # tasks lists every task as (job, position of the task in its job).
    tasks = [(j, t) for j, job in enumerate(jobs_data) for t in range(len(job))]
    machine = {(j, t): jobs_data[j][t][0] for j, t in tasks}   # the machine of each task
    duration = {(j, t): jobs_data[j][t][1] for j, t in tasks}  # the duration of each task

    # horizon is the length of a greedy schedule, which at each step starts the job whose next
    # task can begin earliest. The optimal makespan is at most this, and so is every start time
    # in an optimal schedule.
    job_ready = [0] * len(jobs_data)   # the time the last scheduled task of each job ends
    machine_free = {}                  # the time each machine is free again
    next_task = [0] * len(jobs_data)   # the position of the next unscheduled task of each job
    for _ in tasks:
        candidates = [(max(job_ready[j], machine_free.get(machine[j, next_task[j]], 0)), j)
                      for j in range(len(jobs_data)) if next_task[j] < len(jobs_data[j])]
        begin, j = min(candidates)
        t = next_task[j]
        job_ready[j] = machine_free[machine[j, t]] = begin + duration[j, t]
        next_task[j] += 1
    horizon = max(job_ready)

    # head[task] is the total duration of the earlier tasks of its job, and tail[task] the
    # total duration of the later ones.
    head = {(j, t): sum(duration[j, s] for s in range(t)) for j, t in tasks}
    tail = {(j, t): sum(duration[j, s] for s in range(t + 1, len(jobs_data[j]))) for j, t in tasks}
    # on_machine[m] lists the tasks on machine m.
    on_machine = {}
    for task in tasks:
        on_machine.setdefault(machine[task], []).append(task)
    # head_min[m] and tail_min[m] are the least head and the least tail of the tasks on machine m.
    head_min = {m: min(head[task] for task in ts) for m, ts in on_machine.items()}
    tail_min = {m: min(tail[task] for task in ts) for m, ts in on_machine.items()}
    # lower is a lower bound on the makespan. A job takes at least the sum of its durations, and
    # a machine takes at least its total work plus the least time its tasks must wait before and
    # after.
    lower = max([sum(d for _, d in job) for job in jobs_data]
                + [head_min[m] + sum(duration[task] for task in ts) + tail_min[m]
                   for m, ts in on_machine.items()])

    solver = Exact()

    # Exact identifies its variables by name.
    # start[task] is the time the task starts, from 0 to the horizon.
    start = {task: f"start_{task[0]}_{task[1]}" for task in tasks}
    for task in tasks:
        solver.addVariable(start[task], 0, horizon)

    # makespan is the time the last task ends, from the lower bound to the horizon.
    solver.addVariable("makespan", min(lower, horizon), horizon)

    # before[a, b] is 1 when task a runs before task b on their machine, and 0 when b runs first.
    before = {}
    for ts in on_machine.values():
        for x in range(len(ts)):
            for y in range(x + 1, len(ts)):
                a, b = ts[x], ts[y]
                before[a, b] = f"task_{a[0]}_{a[1]}_before_{b[0]}_{b[1]}"
                solver.addVariable(before[a, b], 0, 1)

    def precedes(a, b):
        # The order of two tasks on one machine, as (terms, constant): the sum is 1 when a runs
        # before b, and 0 when b runs first.
        if (a, b) in before:
            return [(1, before[a, b])], 0
        return [(-1, before[b, a])], 1

    # A task cannot start before the previous task of its job has ended.
    for j, t in tasks:
        if t > 0:
            solver.addConstraint([(1, start[j, t]), (-1, start[j, t - 1])], True, duration[j, t - 1])

    # Two tasks on one machine do not overlap: the one that runs first ends before the other starts.
    for ts in on_machine.values():
        for x in range(len(ts)):
            for y in range(x + 1, len(ts)):
                a, b = ts[x], ts[y]
                # if a runs first, b starts after a ends
                solver.addConstraint([(1, start[b]), (-1, start[a]), (-horizon, before[a, b])],
                                     True, duration[a] - horizon)
                # if b runs first, a starts after b ends
                solver.addConstraint([(1, start[a]), (-1, start[b]), (horizon, before[a, b])],
                                     True, duration[b])

    # The order on a machine is transitive: for tasks x, y, z on one machine, listed in that
    # order, if x runs before y and y runs before z, then x runs before z.
    for ts in on_machine.values():
        for x in range(len(ts)):
            for y in range(x + 1, len(ts)):
                for z in range(y + 1, len(ts)):
                    solver.addConstraint([(1, before[ts[x], ts[y]]), (1, before[ts[y], ts[z]]),
                                          (-1, before[ts[x], ts[z]])], True, 0, True, 1)

    # The makespan is at least the end of the last task of each job. A job with no tasks is skipped.
    for j, job in enumerate(jobs_data):
        if not job:
            continue
        last = (j, len(job) - 1)
        solver.addConstraint([(1, "makespan"), (-1, start[last])], True, duration[last])

    # A task on a machine starts no earlier than the least head of the machine, plus the
    # durations of the other tasks on the machine that run before it.
    for m, ts in on_machine.items():
        for a in ts:
            terms, rhs = [(1, start[a])], head_min[m]
            for b in ts:
                if b != a and duration[b]:
                    t, c = precedes(b, a)
                    terms += [(-duration[b] * coef, name) for coef, name in t]
                    rhs += duration[b] * c
            solver.addConstraint(terms, True, rhs)

    # The makespan is at least the start of a task on a machine, plus its duration, plus the
    # durations of the other tasks on the machine that run after it, plus the least tail of the
    # machine.
    for m, ts in on_machine.items():
        for a in ts:
            terms, rhs = [(1, "makespan"), (-1, start[a])], duration[a] + tail_min[m]
            for b in ts:
                if b != a and duration[b]:
                    t, c = precedes(a, b)
                    terms += [(-duration[b] * coef, name) for coef, name in t]
                    rhs += duration[b] * c
            solver.addConstraint(terms, True, rhs)

    # Minimise the makespan.
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
