# three_sum: a PyCSP3 model from DCP Rosetta.
# Download the `three_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python three_sum.py three_sum.json

from pycsp3 import *


def create_model(instance):
    """Given a collection of integers, find exactly m elements that sum to zero."""
    nums = instance["nums"]  # nums[i] is the i-th integer of the collection
    m = instance["m"]  # the number of elements to select
    n_nums = len(nums)

    # indices[i] is 1 when the i-th integer is selected
    indices = VarArray(size=n_nums, dom={0, 1})

    satisfy(
        # Exactly m elements are selected.
        Sum(indices) == m,
        # The selected elements sum to zero.
        Sum(nums[i] * indices[i] for i in range(n_nums)) == 0,
    )

    return {"indices": indices}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
