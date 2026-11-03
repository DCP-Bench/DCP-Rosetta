# three_sum: an Exact (Python) model from DCP Rosetta.
# Download the `three_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python three_sum.py three_sum.json

from exact import Exact


def create_model(instance):
    """Given a collection of integers, select a given number of its elements whose
    sum is zero."""
    nums = instance["nums"]  # nums[i]: the i-th integer of the collection
    m = instance["m"]        # how many elements to select
    n_nums = len(nums)       # the number of integers in the collection

    solver = Exact()

    # Exact identifies its variables by name.
    # indices[i] is 1 when the i-th integer is selected, and 0 when not
    indices = [f"indices_{i}" for i in range(n_nums)]
    for name in indices:
        solver.addVariable(name, 0, 1)

    # The selected integers sum to zero.
    solver.addConstraint([(nums[i], indices[i]) for i in range(n_nums) if nums[i]], True, 0, True, 0)

    # Exactly m integers are selected.
    solver.addConstraint([(1, name) for name in indices], True, m, True, m)

    return solver, {"indices": indices}


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
