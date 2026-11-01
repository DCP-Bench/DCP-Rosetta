# resource_constrained_project_scheduling: a CPMpy model from DCP Rosetta.
# Download the `resource_constrained_project_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python resource_constrained_project_scheduling.py resource_constrained_project_scheduling.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Schedule jobs with given durations and resource needs so that every precedence
    holds and no resource is used beyond its capacity at any time, with the project
    finishing as early as possible."""
    durations = np.array(instance["durations_data"])      # durations[j]: how long job j takes
    needs = np.array(instance["resource_needs_data"])     # needs[j][r]: units of resource r that job j uses while running
    capacities = instance["resource_capacities_data"]     # capacities[r]: units of resource r available at any time
    precedences = instance["successors_link_data"]        # [a, b]: job b may only start once job a has finished

    # start_time[j] is when job j starts. Running all jobs one after the other is always
    # feasible, so no job needs to start later than the total duration.
    horizon = durations.sum()
    start_time = cp.intvar(0, horizon, shape=len(durations), name="start_time")

    model = cp.Model()
    # Precedence: job b starts after job a has finished.
    for a, b in precedences:
        model.add(start_time[b] >= start_time[a] + durations[a])
    # Resource capacity: the jobs running together need no more of a resource than is available.
    for r, capacity in enumerate(capacities):
        model.add(cp.Cumulative(start=start_time,
                               duration=durations,
                               end=start_time + durations,
                               demand=needs[:, r],
                               capacity=capacity))

    # Minimise the project end. The last job is a dummy of duration 0 that follows all
    # others, so the project ends when the latest job starts.
    model.minimize(cp.max(start_time))

    return model, {"start_time": start_time}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
