# three_sum: a Choco-solver (Python) model from DCP Rosetta.
# Download the `three_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python three_sum.py three_sum.json

from pychoco.model import Model


def create_model(instance):
    """Given a collection of integers, find a given number of its elements that sum to zero."""
    nums = instance["nums"]  # nums[i]: the i-th integer of the collection
    m = instance["m"]        # how many elements to select

    model = Model()

    # indices[i] is true when element i is selected
    indices = [model.boolvar(name=f"i{i}") for i in range(len(nums))]

    # The selected elements sum to zero.
    model.scalar(indices, nums, "=", 0).post()

    # Exactly m elements are selected.
    model.sum(indices, "=", m).post()

    return model, {"indices": indices}, None


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
