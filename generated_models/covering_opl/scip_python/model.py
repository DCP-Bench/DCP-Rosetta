# covering_opl: a SCIP (Python) model from DCP Rosetta.
# Download the `covering_opl.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python covering_opl.py covering_opl.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Choose which workers to hire so that every task is performed by at least
    one hired worker who is qualified for it, at the smallest total hiring cost.

    Returns (model, outputs). outputs["total_cost"] is the total hiring cost of
    the hired workers. outputs["workers"] has one entry per worker, 1 when that
    worker is hired and 0 when not.
    """
    # nb_workers: how many workers there are. The workers are numbered 1 to nb_workers.
    nb_workers = instance["nb_workers"]
    # Cost: Cost[k - 1] is the hiring cost of worker k, since the list is in worker order.
    cost = instance["Cost"]
    # Qualified: one list per task, holding the numbers of the workers who can perform that task.
    # The numbers start at 1, so worker k sits at position k - 1 in the model's lists.
    # The rows differ in length, so they are used as plain lists, not as a matrix.
    qualified = instance["Qualified"]

    model = Model("covering_opl")

    # hired[k - 1] is 1 when worker k is hired and 0 when not. Each worker is hired or not,
    # so the variable is binary.
    hired = [model.addVar(name=f"hired_{k}", vtype="B") for k in range(1, nb_workers + 1)]

    # Every task is performed: for each task, at least one of the workers qualified for it is hired.
    for task_workers in qualified:
        model.addCons(quicksum(hired[k - 1] for k in task_workers) >= 1)

    # total_cost: the hiring cost of the hired workers, the sum of Cost over the hired workers.
    total_cost = quicksum(c * h for c, h in zip(cost, hired))

    # Minimise the total hiring cost.
    model.setObjective(total_cost, "minimize")

    return model, {"total_cost": total_cost, "workers": hired}


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
