# resource_constrained_project_scheduling: an Exact (Python) model from DCP Rosetta.
# Download the `resource_constrained_project_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python resource_constrained_project_scheduling.py resource_constrained_project_scheduling.json

from exact import Exact


def create_model(instance):
    """Start each job so that every precedence holds, the jobs running at any time need no
    more of each resource than its capacity, and the project finishes as early as possible,
    which means the latest start time is as small as possible."""
    durations = instance["durations_data"]              # durations[j]: how long job j runs
    needs = instance["resource_needs_data"]             # needs[j][r]: units of resource r that job j uses while it runs
    capacities = instance["resource_capacities_data"]   # capacities[r]: units of resource r available at any time
    links = instance["successors_link_data"]            # [a, b]: job b can start only after job a has finished
    n_jobs = len(durations)
    n_resources = len(capacities)

    # preds[j] are the jobs that must finish before job j starts, and succs[j] the jobs that wait for job j
    preds = [[] for _ in range(n_jobs)]
    succs = [[] for _ in range(n_jobs)]
    for a, b in links:
        succs[a].append(b)
        preds[b].append(a)

    # order lists the jobs so that each job comes after its predecessors
    order = []
    waiting = [len(preds[j]) for j in range(n_jobs)]  # waiting[j]: predecessors of job j not yet in order
    ready = [j for j in range(n_jobs) if waiting[j] == 0]
    while ready:
        j = ready.pop()
        order.append(j)
        for s in succs[j]:
            waiting[s] -= 1
            if waiting[s] == 0:
                ready.append(s)

    # earliest[j] is the earliest time job j can start when only the precedences are counted
    earliest = [0] * n_jobs
    for j in order:
        for s in succs[j]:
            earliest[s] = max(earliest[s], earliest[j] + durations[j])

    # tail[j] is the longest time from the start of job j to the start of a job that must follow it
    tail = [0] * n_jobs
    for j in reversed(order):
        for s in succs[j]:
            tail[j] = max(tail[j], durations[j] + tail[s])

    # Greedy schedule. Jobs are placed one at a time, the job with the longest tail first, each
    # at the earliest time that its predecessors allow and at which its resources are free.
    # used[r][u] is the amount of resource r taken at time u by the jobs placed so far.
    used = [[0] * (2 * sum(durations) + 2) for _ in range(n_resources)]
    greedy_start = [None] * n_jobs
    for _ in range(n_jobs):
        eligible = [j for j in range(n_jobs)
                    if greedy_start[j] is None and all(greedy_start[p] is not None for p in preds[j])]
        j = max(eligible, key=lambda k: (tail[k], -k))
        t = max([greedy_start[p] + durations[p] for p in preds[j]], default=0)
        while any(used[r][u] + needs[j][r] > capacities[r]
                  for r in range(n_resources) for u in range(t, t + durations[j])):
            t += 1
        for r in range(n_resources):
            for u in range(t, t + durations[j]):
                used[r][u] += needs[j][r]
        greedy_start[j] = t

    # horizon is the latest start in that schedule, so no optimal project starts a job later
    horizon = max(greedy_start)
    # latest[j] is the latest time job j can start and still leave time for the jobs that follow it
    latest = [horizon - tail[j] for j in range(n_jobs)]

    solver = Exact()

    # Exact identifies its variables by name.
    # start_time[j] is the time job j starts, within its earliest and latest start
    start_time = [f"start_{j}" for j in range(n_jobs)]
    for j in range(n_jobs):
        solver.addVariable(start_time[j], earliest[j], latest[j])

    # started_by[j][t] is 1 when job j has started by time t, and 0 before that.
    # It is 0 before the earliest start and 1 from the latest start on.
    started_by = [[f"job_{j}_started_by_{t}" for t in range(horizon + 1)] for j in range(n_jobs)]
    for j in range(n_jobs):
        for t in range(horizon + 1):
            solver.addVariable(started_by[j][t], 1 if t >= latest[j] else 0, 0 if t < earliest[j] else 1)
        # once started, a job stays started
        for t in range(earliest[j], latest[j]):
            solver.addConstraint([(1, started_by[j][t]), (-1, started_by[j][t + 1])], False, 0, True, 0)
        # the job is started at every time from its start on, so the start time and the number of
        # times in its window at which it has started add up to the latest start
        solver.addConstraint([(1, start_time[j])] + [(1, started_by[j][t]) for t in range(earliest[j], latest[j])],
                             True, latest[j], True, latest[j])

    # job b starts only after job a has finished: if b has started by time t, then a has started
    # by time t minus the duration of a
    for a, b in links:
        for t in range(earliest[b], latest[b]):
            solver.addConstraint([(1, started_by[b][t]), (-1, started_by[a][t - durations[a]])],
                                 False, 0, True, 0)

    # at every time, the jobs running then use no more of each resource than its capacity.
    # Job j is running at time t when it started within the durations[j] times up to t.
    for r in range(n_resources):
        for t in range(horizon + 1):
            terms = []
            for j in range(n_jobs):
                if durations[j] == 0 or needs[j][r] == 0:
                    continue
                if not earliest[j] <= t <= latest[j] + durations[j] - 1:
                    continue
                terms.append((needs[j][r], started_by[j][t]))
                if t - durations[j] >= 0:
                    terms.append((-needs[j][r], started_by[j][t - durations[j]]))
            if sum(c for c, _ in terms if c > 0) > capacities[r]:
                solver.addConstraint(terms, False, 0, True, capacities[r])

    # the makespan is the project end, which is the latest start over all jobs
    solver.addVariable("makespan", max(earliest), horizon)
    for j in range(n_jobs):
        solver.addConstraint([(1, "makespan"), (-1, start_time[j])], True, 0)

    # Finish the project as early as possible.
    solver.setObjective([(1, "makespan")], minimize=True)

    return solver, {"start_time": start_time}


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
