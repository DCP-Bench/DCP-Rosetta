# three_sum: a Z3 (Python) model from DCP Rosetta.
# Download the `three_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python three_sum.py three_sum.json

import z3


def create_model(instance):
    """Given a collection of integers, find a given number of its elements that
    sum to zero."""
    nums = instance["nums"]          # nums[i]: the i-th integer of the collection
    n_nums = len(nums)               # the number of integers in the collection
    n_selected = instance["m"]       # how many elements to select

    # indices[i] is true when element i is selected
    indices = [z3.Bool(f"i_{i}") for i in range(n_nums)]

    # picked[i] is 1 when element i is selected, and 0 otherwise
    picked = [z3.If(indices[i], 1, 0) for i in range(n_nums)]

    solver = z3.Solver()

    # The selected elements sum to zero.
    solver.add(z3.Sum([nums[i] * picked[i] for i in range(n_nums)]) == 0)

    # Exactly the wanted number of elements is selected.
    solver.add(z3.Sum(picked) == n_selected)

    return solver, {"indices": indices}


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
