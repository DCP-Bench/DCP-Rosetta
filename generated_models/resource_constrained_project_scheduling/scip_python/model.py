# resource_constrained_project_scheduling: a SCIP (Python) model from DCP Rosetta.
# Download the `resource_constrained_project_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python resource_constrained_project_scheduling.py resource_constrained_project_scheduling.json

from pyscipopt import Model


def create_model(instance):
    """Schedule the jobs of a project so that the whole project finishes as early as possible.

    Each job runs once, without interruption, for its duration. Some jobs must finish
    before others may start (precedence). Each job uses an amount of each
    resource while it runs, and at every time the running jobs together may not use more
    of a resource than its capacity. Choose the start time of every job so that the
    makespan, the finish time of the project, is as small as possible.
    """
    # durations[j]: how many time units job j runs
    durations = instance["durations_data"]
    # needs[j][r]: how much of resource r job j uses while it runs
    needs = instance["resource_needs_data"]
    # capacities[r]: how much of resource r is available at any time
    capacities = instance["resource_capacities_data"]
    # [i, j]: job i must finish before job j may start
    precedences = instance["successors_link_data"]

    n_jobs = len(durations)
    n_resources = len(capacities)
    # Upper bound for every start time and for the makespan, derived from the data: running
    # the jobs one after another takes sum(durations) time units. That serial schedule meets
    # the capacities whenever each job's needs fit them (if one does not fit, no schedule
    # exists), and an optimal schedule finishes no later than it.
    horizon = sum(durations)

    model = Model("resource_constrained_project_scheduling")

    # start[j] is the start time of job j, counted from 0 at the start of the project
    start = [model.addVar(f"start_{j}", vtype="I", lb=0, ub=horizon) for j in range(n_jobs)]

    # makespan is the finish time of the project. Constraints below keep it at or above every
    # job's finish time, and minimising it makes it equal to the latest finish.
    makespan = model.addVar("makespan", vtype="I", lb=0, ub=horizon)

    # Precedence: job j starts only once job i has finished, at start[i] + durations[i] or later.
    for i, j in precedences:
        model.addCons(start[j] >= start[i] + durations[i])

    # Resources: at every time, the jobs running together use at most the capacity of each
    # resource. SCIP's cumulative constraint states this for one resource, given the start
    # variables and the constant durations and needs, so it is posted once per resource.
    for r in range(n_resources):
        model.addConsCumulative(start, durations, [needs[j][r] for j in range(n_jobs)], capacities[r])

    # Makespan: the project finishes no earlier than every job's finish time.
    for j in range(n_jobs):
        model.addCons(makespan >= start[j] + durations[j])

    # Objective: minimise the makespan, the finish time of the project.
    model.setObjective(makespan, "minimize")

    return model, {"start_time": start}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
