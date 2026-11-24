# knapsack: a PyCSP3 model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python knapsack.py knapsack.json

from pycsp3 import *


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    item_values = instance["values"]    # item_values[i] is the value of item i
    item_weights = instance["weights"]  # item_weights[i] is the weight of item i
    capacity = instance["capacity"]     # the most weight the backpack can carry
    n_items = len(item_values)

    # x[i] is 1 when the hiker packs item i
    x = VarArray(size=n_items, dom={0, 1}, id="x")

    # The packed items weigh no more than the backpack can carry.
    satisfy(Sum(item_weights[i] * x[i] for i in range(n_items)) <= capacity)

    # Pack the most valuable selection.
    maximize(Sum(item_values[i] * x[i] for i in range(n_items)))

    return {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
