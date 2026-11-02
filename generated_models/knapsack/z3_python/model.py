# knapsack: a Z3 (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python knapsack.py knapsack.json

import z3


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    # x[i] is true when the hiker packs item i
    x = [z3.Bool(f"x_{i}") for i in range(len(values))]

    solver = z3.Optimize()

    # The packed items weigh no more than the backpack can carry.
    solver.add(z3.Sum([z3.If(xi, w, 0) for w, xi in zip(weights, x)]) <= capacity)

    # Pack the most valuable selection.
    packed_value = z3.Sum([z3.If(xi, v, 0) for v, xi in zip(values, x)])
    solver.maximize(packed_value)

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
