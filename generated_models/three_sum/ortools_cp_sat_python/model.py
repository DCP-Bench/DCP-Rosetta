# three_sum: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `three_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
# Then run it on the first instance (after `pip install ortools`):
#   python three_sum.py three_sum.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Given a collection of integers, find a given number of its elements that
    sum to zero."""
    nums = instance["nums"]        # nums[i]: the i-th integer of the collection
    n_elements = instance["m"]     # how many elements to select

    model = cp_model.CpModel()

    # indices[i] is true when element i is selected
    indices = [model.new_bool_var(f"i_{i}") for i in range(len(nums))]

    # The selected elements sum to zero.
    model.add(sum(nums[i] * indices[i] for i in range(len(nums))) == 0)
    # Exactly the wanted number of elements is selected.
    model.add(sum(indices) == n_elements)

    return model, {"indices": indices}


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
