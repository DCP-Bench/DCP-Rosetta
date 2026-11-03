# three_sum: a Python-MIP (Python) model from DCP Rosetta.
# Download the `three_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python three_sum.py three_sum.json

import mip


def create_model(instance):
    """Given a collection of integers, select a given number of them whose sum is zero."""
    nums = instance["nums"]        # nums[i] is the i-th integer of the collection
    m = instance["m"]              # how many elements to select
    n_numbers = len(nums)          # the number of integers in the collection

    model = mip.Model(solver_name="CBC")

    # indices[i] is 1 when integer i is selected
    indices = [model.add_var(f"x_{i}", var_type=mip.BINARY) for i in range(n_numbers)]

    # Exactly m integers are selected.
    model += mip.xsum(indices) == m

    # The selected integers sum to zero.
    model += mip.xsum(nums[i] * indices[i] for i in range(n_numbers)) == 0

    return model, {"indices": indices}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
