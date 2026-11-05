# covering_opl: a hermax (Python) model from DCP Rosetta.
# Download the `covering_opl.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
# Then run it on the first instance (after `pip install hermax`):
#   python covering_opl.py covering_opl.json

"""
Set covering with hiring costs: choose a set of workers so that every task is
performed by at least one hired worker qualified for it, at the lowest total
hiring cost.
"""
from hermax.model import Model


def create_model(instance):
    # nb_workers: how many workers there are
    nb_workers = instance["nb_workers"]
    # num_tasks: how many tasks must be performed
    num_tasks = instance["num_tasks"]
    # Cost[i]: the hiring cost of worker i+1 (0-based index i)
    cost = instance["Cost"]
    # Qualified[t]: the workers who can perform task t, numbered from 1
    qualified = instance["Qualified"]

    m = Model()

    # hire[i] is true when worker i+1 is hired
    hire = m.bool_vector("hire", nb_workers)

    # Every task is performed: at least one hired worker is qualified for it.
    for t in range(num_tasks):
        m &= (sum(hire[w - 1] for w in qualified[t]) >= 1)

    # Total hiring cost of the hired workers, to be minimised.
    total_cost = sum(cost[i] * hire[i] for i in range(nb_workers))
    m.obj += total_cost

    # The objective in the problem's terms: the total hiring cost, the cost minimised above.
    return m, {"total_cost": total_cost, "workers": hire}, total_cost


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
        print("objective =", result[objective])
    else:
        print("No solution:", result.status)
