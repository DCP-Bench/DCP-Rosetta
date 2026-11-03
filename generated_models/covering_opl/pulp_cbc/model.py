# covering_opl: a PuLP (Python) model from DCP Rosetta.
# Download the `covering_opl.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python covering_opl.py covering_opl.json

import pulp


def create_model(instance):
    """Select a set of workers to perform all the tasks while minimizing the cost.
    Each worker can perform certain tasks and has a hiring cost; every task has to be
    performed."""
    n_workers = instance["nb_workers"]  # the number of workers
    cost = instance["Cost"]             # cost[i]: the hiring cost of worker i
    # qualified[t]: the workers who can perform task t
    qualified = [[worker - 1 for worker in task] for task in instance["Qualified"]]

    problem = pulp.LpProblem("covering", pulp.LpMinimize)

    # hired[i] is 1 when worker i is hired, and 0 when not
    hired = [pulp.LpVariable(f"worker_{i}", cat="Binary") for i in range(n_workers)]
    # total_cost is the hiring cost of the hired workers, at most the cost of hiring everyone
    total_cost = pulp.LpVariable("total_cost", 0, sum(cost), cat="Integer")

    # total_cost is the sum of the hiring costs of the hired workers.
    problem += total_cost == pulp.lpSum(cost[i] * hired[i] for i in range(n_workers))

    # Each task is performed by at least one hired worker who is qualified for it.
    for task_workers in qualified:
        problem += pulp.lpSum(hired[worker] for worker in task_workers) >= 1

    # Hire at the lowest total cost.
    problem += total_cost

    return problem, {"total_cost": total_cost, "workers": hired}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
