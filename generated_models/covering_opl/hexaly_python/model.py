"""Covering: hire workers so that every task has a qualified worker, at minimum hiring cost.

Each task lists the workers able to perform it, and each worker has a hiring cost.
"""
import hexaly.optimizer as hx


def build(instance):
    # nb_workers: number of workers; Qualified[t]: the workers qualified for task t, numbered from 1 (rows differ in length)
    # Cost[w]: hiring cost of worker w (0-indexed)
    n_workers, qualified, cost = instance["nb_workers"], instance["Qualified"], instance["Cost"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # workers[w] = 1 if worker w is hired
    workers = [model.bool() for _ in range(n_workers)]

    # Every task is performed: one of the workers qualified for it (numbered from 1) is hired
    # (the "- 1" turns the 1-based worker number into an index into workers)
    for task_workers in qualified:
        model.constraint(model.sum(workers[w - 1] for w in task_workers) >= 1)

    # Minimise the total hiring cost of the hired workers; total_cost is also the reported cost
    total_cost = model.sum(cost[w] * workers[w] for w in range(n_workers))
    model.minimize(total_cost)
    return optimizer, {"total_cost": total_cost, "workers": workers}
