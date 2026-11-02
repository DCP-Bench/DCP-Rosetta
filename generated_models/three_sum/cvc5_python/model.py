# three_sum: a cvc5 (Python) model from DCP Rosetta.
# Download the `three_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python three_sum.py three_sum.json

import cvc5.pythonic as c5


def create_model(instance):
    """Given a collection of integers, find a given number of its elements that sum to zero."""
    nums = instance["nums"]  # nums[i]: the i-th integer of the collection
    m = instance["m"]        # how many elements to select

    # indices[i] is true when element i is selected
    indices = [c5.Bool(f"indices_{i}") for i in range(len(nums))]

    solver = c5.Solver()

    # Exactly m elements are selected.
    solver.add(c5.Sum([c5.If(b, 1, 0) for b in indices]) == m)

    # The selected elements sum to zero.
    solver.add(c5.Sum([c5.If(b, nums[i], 0) for i, b in enumerate(indices)]) == 0)

    return solver, {"indices": indices}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
