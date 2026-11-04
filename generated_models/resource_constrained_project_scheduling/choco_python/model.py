# resource_constrained_project_scheduling: a Choco-solver (Python) model from DCP Rosetta.
# Download the `resource_constrained_project_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python resource_constrained_project_scheduling.py resource_constrained_project_scheduling.json

from pychoco.model import Model


def create_model(instance):
    """Start the jobs of a project so that every job begins after the jobs it depends on
    have ended, and the jobs running at the same time never use more of a resource than
    is available. The project should finish as early as possible."""
    durations = instance["durations_data"]                      # durations[j]: how long job j takes
    resource_needs = instance["resource_needs_data"]            # resource_needs[j][r]: units of resource r that job j uses while it runs
    resource_capacities = instance["resource_capacities_data"]  # resource_capacities[r]: units of resource r available at any time
    successors_link = instance["successors_link_data"]          # pairs [i, j]: job j can start only after job i has ended
    n_jobs = len(durations)
    n_resources = len(resource_capacities)

    model = Model()

    # No job starts later than the time needed to run all the jobs one after another.
    horizon = sum(durations)

    # start_time[j]: the time at which job j starts
    start_time = [model.intvar(0, horizon, name=f"start_{j}") for j in range(n_jobs)]

    # Each job starts no earlier than the jobs it depends on have ended.
    for i, j in successors_link:
        model.arithm(start_time[i], "-", start_time[j], "<=", -durations[i]).post()

    # tasks[j]: job j, occupying its time from its start for its full duration
    tasks = [model.task(start_time[j], durations[j]) for j in range(n_jobs)]

    # At any time, the jobs running together use no more of each resource than its capacity.
    # Jobs with no duration or no need of a resource do not count for that resource.
    for r in range(n_resources):
        users = [j for j in range(n_jobs) if durations[j] > 0 and resource_needs[j][r] > 0]
        if not users:
            continue
        model.cumulative(
            [tasks[j] for j in users],
            [model.intvar(resource_needs[j][r], resource_needs[j][r]) for j in users],
            model.intvar(resource_capacities[r], resource_capacities[r]),
        ).post()

    # makespan: the length of the project, which ends when the latest job starts
    makespan = model.intvar(0, horizon, name="makespan")
    model.max(makespan, start_time).post()

    # Make the project as short as possible.
    return model, {"start_time": start_time}, {"objective": makespan, "maximize": False}


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
