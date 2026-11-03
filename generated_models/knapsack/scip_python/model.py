# knapsack: a SCIP (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python knapsack.py knapsack.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """A hiker is planning a trip and must decide which items to take in the
    backpack: maximise the total value of the items taken, without the items
    weighing more than the backpack's capacity. The instance gives each item's
    value and weight, and the capacity of the backpack."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    model = Model("knapsack")

    # x[i] is 1 when the hiker takes item i, 0 when not
    # (an item is taken whole or not at all, hence binary)
    x = [model.addVar(name=f"x_{i}", vtype="B") for i in range(len(values))]

    # The items taken weigh no more than the backpack's capacity.
    model.addCons(quicksum(w * xi for w, xi in zip(weights, x)) <= capacity)

    # Maximise the total value of the items taken.
    model.setObjective(quicksum(v * xi for v, xi in zip(values, x)), "maximize")

    return model, {"x": x}


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
