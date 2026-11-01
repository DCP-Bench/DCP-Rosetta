# knapsack: a Choco-solver (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python knapsack.py knapsack.json

from pychoco.model import Model


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    model = Model()

    # x[i] is true when the hiker packs item i
    x = [model.boolvar(name=f"x{i}") for i in range(len(values))]

    # The packed items weigh no more than the backpack can carry.
    model.scalar(x, weights, "<=", capacity).post()

    # The total value of the packed items, which the hiker wants as large as possible.
    total_value = model.intvar(0, sum(values), name="total_value")
    model.scalar(x, values, "=", total_value).post()

    return model, {"x": x}, {"objective": total_value, "maximize": True}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
