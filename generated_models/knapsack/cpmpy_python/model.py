# knapsack: a CPMpy model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python knapsack.py knapsack.json

import cpmpy as cp


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    # x[i] is true when the hiker packs item i
    x = cp.boolvar(shape=len(values), name="x")

    model = cp.Model()
    # The packed items weigh no more than the backpack can carry.
    model.add(cp.sum(x * weights) <= capacity)
    # Pack the most valuable selection.
    model.maximize(cp.sum(x * values))

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
