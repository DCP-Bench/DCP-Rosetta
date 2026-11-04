# covering_opl: a Python-MIP (Python) model from DCP Rosetta.
# Download the `covering_opl.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python covering_opl.py covering_opl.json

import mip


def create_model(instance):
    """Select a set of workers to perform all the tasks while minimizing the cost.
    Each worker can perform certain tasks and has a hiring cost; every task has to be
    performed."""
    n_workers = instance["nb_workers"]  # the number of workers
    n_tasks = instance["num_tasks"]     # the number of tasks
    cost = instance["Cost"]             # cost[i]: the hiring cost of worker i
    qualified = instance["Qualified"]   # qualified[t]: the workers who can perform task t

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # hire[i] is 1 when worker i is hired, and 0 when not
    hire = [model.add_var(f"hire_{i}", var_type=mip.BINARY) for i in range(n_workers)]
    # The total hiring cost of the hired workers, at most the cost of hiring everyone.
    total_cost = model.add_var("total_cost", lb=0, ub=sum(cost), var_type=mip.INTEGER)

    # The total cost is the sum of the hiring costs of the hired workers.
    model += total_cost == mip.xsum(cost[i] * hire[i] for i in range(n_workers))

    # Every task is performed: at least one hired worker is qualified for it.
    for t in range(n_tasks):
        model += mip.xsum(hire[w - 1] for w in qualified[t]) >= 1

    # Hire the workers at the lowest total cost.
    model.objective = total_cost

    return model, {"total_cost": total_cost, "workers": hire}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
