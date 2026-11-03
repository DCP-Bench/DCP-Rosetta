# resource_constrained_project_scheduling: a hermax (Python) model from DCP Rosetta.
# Download the `resource_constrained_project_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
# Then run it on the first instance (after `pip install hermax`):
#   python resource_constrained_project_scheduling.py resource_constrained_project_scheduling.json

from hermax.model import Model


def create_model(instance):
    """Schedule the jobs of a project so that every job starts only after its predecessors
    have finished, the jobs running at any time use no more of each resource than its
    capacity, and the project (its makespan) finishes as early as possible."""
    durations = instance["durations_data"]              # durations[j]: how long job j runs
    needs = instance["resource_needs_data"]             # needs[j][r]: how much of resource r job j uses while it runs
    capacities = instance["resource_capacities_data"]   # capacities[r]: how much of resource r is available at any time
    links = instance["successors_link_data"]            # [a, b]: job b may start only after job a has finished
    n = len(durations)
    n_resources = len(capacities)

    # Time bounds derived from the data, so each start time has a narrow domain.
    # Running all jobs one after another is a schedule, so the sum of the durations bounds the makespan.
    horizon = sum(durations)
    # earliest[j]: earliest start of job j allowed by the precedences alone
    earliest = [0] * n
    for _ in range(n):
        for a, b in links:
            earliest[b] = max(earliest[b], earliest[a] + durations[a])
    # tail[j]: length of the longest chain of jobs from job j to the end of the project, j included
    tail = [durations[j] for j in range(n)]
    for _ in range(n):
        for a, b in links:
            tail[a] = max(tail[a], durations[a] + tail[b])
    # The project cannot finish before its longest chain of precedences does.
    lower = max(earliest[j] + durations[j] for j in range(n))

    m = Model()
    # start[j] is the start time of job j (the declared output); it lies between its earliest
    # start and the latest start that still lets the chain of jobs after it finish by the horizon.
    start = [m.int(f"start_{j}", earliest[j], horizon - tail[j]) for j in range(n)]
    # makespan is the finish time of the last job
    makespan = m.int("makespan", lower, horizon)

    # Precedence: job b starts only after job a has finished.
    for a, b in links:
        m &= (start[a] + durations[a] <= start[b])

    # Makespan: the project is finished once every job is finished.
    for j in range(n):
        m &= (start[j] + durations[j] <= makespan)

    # Resources: at any time, the jobs running use no more of a resource than its capacity.
    # Jobs of zero length or that need none of the resource take no part in its constraint.
    for r in range(n_resources):
        users = [j for j in range(n) if durations[j] > 0 and needs[j][r] > 0]
        if users:
            m &= m.cumulative([start[j] for j in users], [durations[j] for j in users],
                              [needs[j][r] for j in users], capacities[r])

    # Objective: minimise the makespan, the finish time of the project.
    m.obj += makespan

    return m, {"start_time": start}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
