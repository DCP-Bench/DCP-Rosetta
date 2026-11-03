# knapsack: an Exact (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python knapsack.py knapsack.json

from exact import Exact


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    solver = Exact()

    # Exact identifies its variables by name.
    # x[i] is 1 when the hiker packs item i, and 0 when not
    x = [f"x{i}" for i in range(len(values))]
    for name in x:
        solver.addVariable(name, 0, 1)

    # The packed items weigh no more than the backpack can carry.
    solver.addConstraint(list(zip(weights, x)), False, 0, True, capacity)

    # Pack the most valuable selection.
    solver.setObjective(list(zip(values, x)), minimize=False)

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
