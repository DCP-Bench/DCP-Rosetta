# three_sum: a CPMpy model from DCP Rosetta.
# Download the `three_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python three_sum.py three_sum.json

import cpmpy as cp


def create_model(instance):
    """Given a collection of integers, find a given number of its elements that sum to zero."""
    nums = instance["nums"]  # nums[i]: the i-th integer of the collection
    m = instance["m"]        # how many elements to select

    # indices[i] is true when element i is selected
    indices = cp.boolvar(shape=len(nums), name="indices")

    model = cp.Model()

    # The selected elements sum to zero.
    model.add(cp.sum(indices * nums) == 0)

    # Exactly m elements are selected.
    model.add(cp.sum(indices) == m)

    return model, {"indices": indices}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
