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
    qualified = instance["Qualified"]  # qualified[task] = list of worker IDs (1-indexed)

    m = Model()

    # Decision variables: whether each worker is selected (indexed 0 to nb_workers-1)
    # workers[i] = True if worker i+1 (1-indexed ID) is selected
    workers = m.bool_vector("workers", nb_workers)

    # Constraint: each task must be covered by at least one selected worker
    for task_id in range(num_tasks):
        # Get the list of workers who can perform this task (1-indexed worker IDs)
        capable_workers_1indexed = qualified[task_id]

        # At least one of the capable workers must be selected
        if capable_workers_1indexed:
            # Convert 1-indexed worker IDs to 0-indexed array indices
            task_covered = sum(workers[w - 1] for w in capable_workers_1indexed)
            m &= (task_covered >= 1)

    # Objective: minimize total cost using soft clauses
    # m.obj[cost] += workers[i] pays cost when workers[i] is false
    # But we want to minimize cost when workers[i] is true
    # So we should use m.obj[cost] += ~workers[i]? No, that pays when false.
    # Actually, for minimization: m.obj[w] += lit pays w when lit is false
    # To minimize when we select a worker, we want to pay the cost when the worker IS selected
    # So we use m.obj[cost] += workers[i] which pays cost when workers[i] is false...
    # Wait, that's wrong. Let me re-think.
    #
    # The solver minimizes total broken weight.
    # m.obj[w] += lit means: if lit is true, there's no cost. If lit is false, pay w.
    # To minimize total cost when workers are selected:
    # We want to pay when workers[i] is true.
    # So we should NOT use workers[i] directly. Instead, use the complement.
    # But we want to minimize, so if workers[i] is true, we LOSE points (pay cost).
    # So m.obj[cost] += workers[i] means we pay cost when workers[i] is FALSE.
    # That's backwards!
    #
    # Actually, wait. The polarity in hermax for MinSAT is that higher cost = worse solution.
    # So to minimize cost when a worker is selected, we use:
    # m.obj[cost] += workers[i] which means we DON'T pay when workers[i] is true (lit is true = no cost)
    # and we DO pay when workers[i] is false.
    # That's still backwards!
    #
    # Let me re-read the skill example:
    # m.obj[cost[i][j]] += ~x[i][j] charges cost for using pairing (i,j)
    # So ~x[i][j] (not x) is used to charge when x is TRUE.
    # So to minimize cost of selecting a worker, I should use:
    # m.obj[cost] += ~workers[i]

    for i in range(nb_workers):
        m.obj[costs[i]] += ~workers[i]

    # Total cost as sum of selected worker costs
    total_cost = sum(costs[i] * workers[i] for i in range(nb_workers))

    return m, {"total_cost": total_cost, "workers": workers}
