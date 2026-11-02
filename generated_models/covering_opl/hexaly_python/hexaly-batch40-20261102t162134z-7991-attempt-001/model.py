"""Covering: hire workers so that every task has a qualified worker, at minimum hiring cost."""
import hexaly.optimizer as hx


def build(instance):
    n_workers, qualified, cost = instance["nb_workers"], instance["Qualified"], instance["Cost"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # workers[w] = 1 if worker w is hired
    workers = [model.bool() for _ in range(n_workers)]

    # Every task is performed: one of the workers qualified for it (numbered from 1) is hired
    for task_workers in qualified:
        model.constraint(model.sum(workers[w - 1] for w in task_workers) >= 1)

    # Minimise the total hiring cost
    total_cost = model.sum(cost[w] * workers[w] for w in range(n_workers))
    model.minimize(total_cost)
    return optimizer, {"total_cost": total_cost, "workers": workers}
