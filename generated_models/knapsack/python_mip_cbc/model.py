# knapsack: a Python-MIP (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python knapsack.py knapsack.json

import mip


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # x[i] is 1 when the hiker packs item i, and 0 when not
    x = [model.add_var(f"x_{i}", var_type=mip.BINARY) for i in range(len(values))]

    # The packed items weigh no more than the backpack can carry.
    model += mip.xsum(w * xi for w, xi in zip(weights, x)) <= capacity

    # Pack the most valuable selection.
    model.objective = mip.xsum(v * xi for v, xi in zip(values, x))

    return model, {"x": x}


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
