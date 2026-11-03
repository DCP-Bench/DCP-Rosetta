# knapsack: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install ortools`):
#   python knapsack.py knapsack.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    model = cp_model.CpModel()

    # x[i] is true when the hiker packs item i
    x = [model.new_bool_var(f"x_{i}") for i in range(len(values))]

    # The packed items weigh no more than the backpack can carry.
    model.add(sum(w * xi for w, xi in zip(weights, x)) <= capacity)
    # Pack the most valuable selection.
    model.maximize(sum(v * xi for v, xi in zip(values, x)))

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
