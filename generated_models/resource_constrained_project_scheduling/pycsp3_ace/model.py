# resource_constrained_project_scheduling: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
# Download the `resource_constrained_project_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python resource_constrained_project_scheduling.py resource_constrained_project_scheduling.json

from pycsp3 import *


def create_model(instance):
    """Jobs, each with a duration and a need of each resource, are scheduled so that a job
    starts only after its predecessors have finished, and the use of each resource never
    exceeds its capacity. Minimise the makespan, the time at which the last job finishes."""
    durations = instance["durations_data"]              # durations[i] is the duration of job i
    needs = instance["resource_needs_data"]             # needs[i][k] is the amount of resource k that job i uses while it runs
    capacities = instance["resource_capacities_data"]   # capacities[k] is the capacity of resource k
    precedences = instance["successors_link_data"]      # [pred, succ]: job succ starts after job pred has finished
    n_jobs = len(durations)

    # Running the jobs one after another, in an order that respects the precedences, finishes by the sum of the durations (taken as non-negative), and an optimal schedule is no longer than that, so no job starts after the sum. It is the horizon.
    horizon = sum(durations)

    # start_time[i] is the start time of job i, counted from 0.
    start_time = VarArray(size=n_jobs, dom=range(horizon + 1))

    satisfy(
        # A job starts only after each of its predecessors has finished.
        [start_time[succ] >= start_time[pred] + durations[pred] for pred, succ in precedences],
        # At every time the jobs running use no more of each resource than its capacity.
        [Cumulative(origins=start_time, lengths=durations, heights=resource_needs) <= capacity
         for capacity, resource_needs in zip(capacities, columns(needs))],
    )

    # The project ends as early as possible: minimise the time at which the last job finishes.
    minimize(Maximum(start_time[i] + durations[i] for i in range(n_jobs)))

    return {"start_time": start_time}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
