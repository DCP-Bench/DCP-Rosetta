"""
Model for covering_opl problem.

Select a set of workers to perform all tasks while minimizing cost.
Each worker has a cost and can perform certain tasks.
All tasks must be covered by at least one selected worker.

Objective: minimize total cost.
"""
from hermax.model import Model


def build(instance):
    nb_workers = instance["nb_workers"]
    num_tasks = instance["num_tasks"]
    costs = instance["Cost"]
    qualified = instance["Qualified"]  # qualified[task] = list of worker indices who can do it

    m = Model()

    # Decision variables: whether each worker is selected
    workers = m.bool_vector("workers", nb_workers)

    # Constraint: each task must be covered by at least one selected worker
    for task_id in range(num_tasks):
        # Get the list of workers who can perform this task
        capable_workers = qualified[task_id]

        # At least one of the capable workers must be selected
        if capable_workers:
            # capable_workers contains worker indices (1-indexed based on instance format)
            # Convert to 0-indexed for our workers array
            task_covered = sum(workers[w - 1] for w in capable_workers)
            m &= (task_covered >= 1)

    # Objective: minimize total cost
    # Pay cost for each selected worker using soft clauses
    for i in range(nb_workers):
        m.obj[costs[i]] += workers[i]

    # Calculate total cost as a linear expression
    # total_cost = sum of costs for selected workers
    total_cost = sum(costs[i] * workers[i] for i in range(nb_workers))

    return m, {"total_cost": total_cost, "workers": workers}
