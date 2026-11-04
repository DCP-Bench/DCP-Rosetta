# jobshop: a Choco-solver (Python) model from DCP Rosetta.
# Download the `jobshop.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python jobshop.py jobshop.json

from itertools import combinations

from pychoco.model import Model


def greedy_makespan(jobs):
    """Length of a schedule built greedily: repeatedly start the next task, among the
    next task of each job, that can start earliest."""
    next_task = [0] * len(jobs)  # position of the next unscheduled task of each job
    job_ready = [0] * len(jobs)  # time at which the last scheduled task of each job ends
    machine_ready = {}  # time at which each machine is free again
    while True:
        # (earliest start, job) of the best next task found so far
        best = None
        for j, job in enumerate(jobs):
            if next_task[j] < len(job):
                machine, _ = job[next_task[j]]
                start = max(job_ready[j], machine_ready.get(machine, 0))
                if best is None or start < best[0]:
                    best = (start, j)
        if best is None:
            return max(job_ready, default=0)
        start, j = best
        machine, duration = jobs[j][next_task[j]]
        job_ready[j] = machine_ready[machine] = start + duration
        next_task[j] += 1


def create_model(instance):
    """Jobs are chains of tasks, each task on one machine for a fixed time, run in order.
    A machine works on one task at a time, a task runs without interruption, and the
    makespan is the time at which the last job finishes; minimize it."""
    jobs = instance["jobs_data"]  # jobs[j][k] is (machine, duration) of task k of job j

    # Total duration of the tasks on each machine.
    machine_load = {}
    for job in jobs:
        for machine, duration in job:
            machine_load[machine] = machine_load.get(machine, 0) + duration

    # The makespan is at least the work of the busiest machine and the work of the longest job.
    lower_bound = max(list(machine_load.values()) + [sum(d for _, d in job) for job in jobs])
    # The makespan is at most the length of a greedy schedule.
    horizon = greedy_makespan(jobs)

    model = Model()

    # tasks[j, k] = (start time, duration, machine) of task k of job j
    tasks = {}
    # on_machine[machine] = the (job, task) keys of the tasks that run on that machine
    on_machine = {}
    for j, job in enumerate(jobs):
        before = 0  # work of job j that comes before its current task
        after = sum(d for _, d in job)  # work of job j from its current task on
        for k, (machine, duration) in enumerate(job):
            # The start time of task k of job j: after the earlier tasks of its job,
            # with room left for the later ones.
            start = model.intvar(before, horizon - after, name=f"start_{j}_{k}")
            tasks[j, k] = (start, duration, machine)
            on_machine.setdefault(machine, []).append((j, k))
            before += duration
            after -= duration

    # A task starts only after the previous task of its job has ended.
    for j, job in enumerate(jobs):
        for k in range(1, len(job)):
            start, _, _ = tasks[j, k]
            previous, previous_duration, _ = tasks[j, k - 1]
            model.arithm(start, "-", previous, ">=", previous_duration).post()

    # Two tasks on the same machine do not overlap: one of them ends before the other starts.
    for keys in on_machine.values():
        for a, b in combinations(keys, 2):
            start_a, duration_a, _ = tasks[a]
            start_b, duration_b, _ = tasks[b]
            # a_first is true when task a ends before task b starts, and b_first the other way round.
            a_first = model.arithm(start_b, "-", start_a, ">=", duration_a).reify()
            b_first = model.arithm(start_a, "-", start_b, ">=", duration_b).reify()
            model.arithm(a_first, "+", b_first, "=", 1).post()

    # Each task needs one unit of its machine, and a machine has one unit.
    one = model.intvar(1, 1, name="one")
    # The same rule for each machine as a whole, so that all its tasks are checked together.
    for keys in on_machine.values():
        machine_tasks = [model.task(tasks[key][0], tasks[key][1]) for key in keys]
        model.cumulative(machine_tasks, [one] * len(machine_tasks), one).post()

    # Each task starts as early as its job and its machine allow: at time 0, or right when
    # the previous task of its job ends, or right when another task on its machine ends.
    # Moving a task earlier this way never lengthens a schedule.
    for (j, k), (start, _, machine) in tasks.items():
        options = []
        if k == 0:
            options.append(model.arithm(start, "=", 0))
        else:
            previous, previous_duration, _ = tasks[j, k - 1]
            options.append(model.arithm(start, "-", previous, "=", previous_duration))
        for other in on_machine[machine]:
            if other != (j, k):
                other_start, other_duration, _ = tasks[other]
                options.append(model.arithm(start, "-", other_start, "=", other_duration))
        model.or_(options).post()

    # The makespan, between the lower bound and the greedy length.
    makespan = model.intvar(lower_bound, horizon, name="makespan")
    # end[j] is the time at which job j finishes its last task.
    last_ends = []
    for j, job in enumerate(jobs):
        start, duration, _ = tasks[j, len(job) - 1]
        end = model.intvar(0, horizon, name=f"end_{j}")
        model.arithm(end, "-", start, "=", duration).post()
        last_ends.append(end)
    # The makespan is the latest finish time of the jobs.
    model.max(makespan, last_ends).post()

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
