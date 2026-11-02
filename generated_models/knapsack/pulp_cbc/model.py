# knapsack: a PuLP (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python knapsack.py knapsack.json

import pulp


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    problem = pulp.LpProblem("knapsack", pulp.LpMaximize)

    # x[i] is 1 when the hiker packs item i, and 0 when not
    x = [pulp.LpVariable(f"x_{i}", cat="Binary") for i in range(len(values))]

    # The packed items weigh no more than the backpack can carry.
    problem += pulp.lpSum(w * xi for w, xi in zip(weights, x)) <= capacity

    # Pack the most valuable selection.
    problem += pulp.lpSum(v * xi for v, xi in zip(values, x))

    return problem, {"x": x}


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
