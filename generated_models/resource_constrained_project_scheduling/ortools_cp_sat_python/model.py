# resource_constrained_project_scheduling: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `resource_constrained_project_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
# Then run it on the first instance (after `pip install ortools`):
#   python resource_constrained_project_scheduling.py resource_constrained_project_scheduling.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Start every job so that the precedence relations hold and, at every moment, the
    jobs running together use no more of each renewable resource than its capacity,
    finishing the project as early as possible."""
    durations = instance["durations_data"]                # durations[j]: how long job j runs
    needs = instance["resource_needs_data"]               # needs[j][r]: units of resource r that job j uses while it runs
    capacities = instance["resource_capacities_data"]     # capacities[r]: units of resource r available at any time
    precedences = instance["successors_link_data"]        # the pairs [a, b] of jobs, job a before job b
    n_jobs = len(durations)
    horizon = sum(durations)  # running the jobs one after another always fits

    model = cp_model.CpModel()

    # start_time[j] is when job j starts
    start_time = [model.new_int_var(0, horizon, f"start_{j}") for j in range(n_jobs)]
    # job j occupies its resource units from start_time[j] for durations[j] time units
    intervals = [
        model.new_fixed_size_interval_var(start_time[j], durations[j], f"job_{j}")
        for j in range(n_jobs)
    ]

    # Precedence: job b starts only after job a has finished.
    for a, b in precedences:
        model.add(start_time[b] >= start_time[a] + durations[a])

    # Capacity: for each resource, the jobs running at any moment need no more units than
    # are available.
    for r, capacity in enumerate(capacities):
        model.add_cumulative(intervals, [row[r] for row in needs], capacity)

    # makespan is the latest start time over all jobs, which is when the project ends.
    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, start_time)
    # Finish the project as early as possible.
    model.minimize(makespan)

    return model, {"start_time": start_time}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
