# resource_constrained_project_scheduling: a PuLP (Python) model from DCP Rosetta.
# Download the `resource_constrained_project_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python resource_constrained_project_scheduling.py resource_constrained_project_scheduling.json

import heapq

import pulp


def create_model(instance):
    """Start the jobs of a project so that each job starts only after its predecessors have
    finished, and at every time the jobs running together use no more of each resource than
    its capacity. The project ends when the last job starts; minimise that time."""
    durations = instance["durations_data"]                # durations[j]: how long job j takes
    needs = instance["resource_needs_data"]               # needs[j][r]: units of resource r that job j uses while it runs
    capacities = instance["resource_capacities_data"]     # capacities[r]: units of resource r available at any time
    precedences = instance["successors_link_data"]        # each pair [a, b]: job b starts only after job a has finished
    n_jobs = len(durations)
    n_resources = len(capacities)

    # predecessors[j] and successors[j]: the jobs that must finish before job j starts, and
    # the jobs that cannot start before job j has finished.
    predecessors = [[] for _ in range(n_jobs)]
    successors = [[] for _ in range(n_jobs)]
    for before, after in precedences:
        predecessors[after].append(before)
        successors[before].append(after)

    # Jobs in an order where every job comes after all its predecessors.
    open_predecessors = [len(p) for p in predecessors]
    order = [j for j in range(n_jobs) if open_predecessors[j] == 0]
    for j in order:
        for k in successors[j]:
            open_predecessors[k] -= 1
            if open_predecessors[k] == 0:
                order.append(k)

    # tail[j]: the longest time from the start of job j to the start of the last job, along a
    # chain of jobs that follow j. The start of job j is at least this much earlier than the
    # start of the last job.
    tail = [0] * n_jobs
    for j in reversed(order):
        for k in successors[j]:
            tail[j] = max(tail[j], durations[j] + tail[k])

    # earliest[j]: the earliest time job j can start when only the precedences are counted.
    earliest = [0] * n_jobs
    for j in order:
        for k in successors[j]:
            earliest[k] = max(earliest[k], earliest[j] + durations[j])

    # A simple schedule gives an upper bound on the latest start of an optimal schedule. Jobs
    # are placed one at a time, the jobs with the longest tail first. Each job starts at the
    # earliest time when its predecessors have finished and the resources are free for its
    # whole duration.
    total_duration = sum(durations)
    # usage[r][t]: units of resource r in use at time t in this schedule
    usage = [[0] * (2 * total_duration + max(durations) + 2) for _ in range(n_resources)]
    # placed[j]: the start time of job j in this schedule
    placed = [None] * n_jobs
    open_predecessors = [len(p) for p in predecessors]
    ready = [(-tail[j], j) for j in range(n_jobs) if open_predecessors[j] == 0]
    heapq.heapify(ready)
    while ready:
        _, j = heapq.heappop(ready)
        start = max([placed[p] + durations[p] for p in predecessors[j]], default=0)
        while any(usage[r][u] + needs[j][r] > capacities[r]
                  for r in range(n_resources) for u in range(start, start + durations[j])):
            start += 1
        placed[j] = start
        for r in range(n_resources):
            for u in range(start, start + durations[j]):
                usage[r][u] += needs[j][r]
        for k in successors[j]:
            open_predecessors[k] -= 1
            if open_predecessors[k] == 0:
                heapq.heappush(ready, (-tail[k], k))

    # The latest start in that schedule. No job starts later in an optimal schedule.
    horizon = max(placed)

    problem = pulp.LpProblem("rcpsp", pulp.LpMinimize)

    # possible_starts[j]: the times job j can start, from its earliest start up to the latest
    # start that still leaves time for the jobs after it.
    possible_starts = {j: range(earliest[j], horizon - tail[j] + 1) for j in range(n_jobs)}
    # first[(j, t)] is 1 when job j starts at time t, and 0 otherwise.
    first = {(j, t): pulp.LpVariable(f"first_{j}_{t}", cat="Binary")
             for j in range(n_jobs) for t in possible_starts[j]}
    # start_time[j]: the time job j starts.
    start_time = [pulp.LpVariable(f"start_{j}", earliest[j], horizon - tail[j], cat="Integer")
                  for j in range(n_jobs)]

    def started_by(j, t):
        """1 when job j has started at time t or earlier, as an expression"""
        return pulp.lpSum(first[(j, u)] for u in possible_starts[j] if u <= t)

    # Each job starts at exactly one time, and start_time[j] is that time.
    for j in range(n_jobs):
        problem += pulp.lpSum(first[(j, t)] for t in possible_starts[j]) == 1
        problem += start_time[j] == pulp.lpSum(t * first[(j, t)] for t in possible_starts[j])

    # Job b starts only after job a has finished: if b has started by time t, then a has
    # started by time t minus its duration.
    for before, after in precedences:
        for t in possible_starts[after]:
            problem += started_by(after, t) <= started_by(before, t - durations[before])

    # At every time, the jobs running then use no more of each resource than its capacity.
    # A job runs for its duration from its start.
    for r in range(n_resources):
        for t in range(horizon + max(durations)):
            in_use = pulp.lpSum(
                needs[j][r] * first[(j, u)]
                for j in range(n_jobs) if needs[j][r] > 0
                for u in possible_starts[j] if t - durations[j] < u <= t)
            problem += in_use <= capacities[r]

    # makespan: the latest start time of any job. The last job is a dummy job of duration 0,
    # so this is the end of the project.
    makespan = pulp.LpVariable("makespan", 0, horizon, cat="Integer")
    for j in range(n_jobs):
        problem += makespan >= start_time[j]
    # Finish the project as early as possible.
    problem += makespan

    return problem, {"start_time": start_time}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
