# resource_constrained_project_scheduling: a Z3 (Python) model from DCP Rosetta.
# Download the `resource_constrained_project_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python resource_constrained_project_scheduling.py resource_constrained_project_scheduling.json

import z3


def create_model(instance):
    """Start every job so that each job begins only after its predecessors have finished,
    no resource is used beyond its capacity at any time, and the project finishes as
    early as possible."""
    durations = instance["durations_data"]             # durations[j]: how long job j takes
    needs = instance["resource_needs_data"]            # needs[j][r]: units of resource r that job j uses while it runs
    capacities = instance["resource_capacities_data"]  # capacities[r]: units of resource r available at any time
    precedences = instance["successors_link_data"]     # [a, b]: job b may start only after job a has finished
    n_jobs = len(durations)
    horizon = sum(durations)  # running the jobs one after another always fits, so no job starts later

    # start_time[j] is when job j starts
    start_time = [z3.Int(f"start_{j}") for j in range(n_jobs)]

    solver = z3.Optimize()

    solver.add(
        # Every job starts within the horizon.
        *[z3.And(start >= 0, start <= horizon) for start in start_time],
        # Job b starts only after job a has finished.
        *[start_time[b] >= start_time[a] + durations[a] for a, b in precedences],
    )

    # Resource use only rises when a job starts, so checking the moments at which jobs
    # start covers every moment. At each such moment, the jobs running then use no more
    # of each resource than is available.
    for r, capacity in enumerate(capacities):
        for j in range(n_jobs):
            # units of resource r used by each job running when job j starts; a job runs
            # from its start up to, not including, its start plus its duration
            running = [
                z3.If(z3.And(start_time[i] <= start_time[j], start_time[j] < start_time[i] + durations[i]), needs[i][r], 0)
                for i in range(n_jobs)
                if durations[i] > 0 and needs[i][r] > 0
            ]
            if running:
                solver.add(z3.Sum(running) <= capacity)

    # makespan is when the project ends. The last job takes no time and follows all others,
    # so the project ends when the latest job starts.
    makespan = z3.Int("makespan")
    solver.add(
        # makespan is the start time of one of the jobs ...
        z3.Or([makespan == start for start in start_time]),
        # ... and no job starts after it.
        *[makespan >= start for start in start_time],
    )

    solver.minimize(makespan)

    return solver, {"start_time": start_time}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
