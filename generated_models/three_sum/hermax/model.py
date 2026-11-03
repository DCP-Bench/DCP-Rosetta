# three_sum: a hermax (Python) model from DCP Rosetta.
# Download the `three_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
# Then run it on the first instance (after `pip install hermax`):
#   python three_sum.py three_sum.json

from hermax.model import Model


def create_model(instance):
    """Given a collection of integers, select exactly m of them so that the selected
    numbers sum to zero. Report, for each element, whether it is selected."""
    nums = instance["nums"]   # nums[i]: the i-th integer of the collection
    count = instance["m"]     # m: how many elements must be selected (the instance's "m" field)
    n = len(nums)             # number of integers in the collection

    m = Model()
    # selected[i] is true when element i is part of the chosen group
    selected = m.bool_vector("selected", n)

    # Exactly m elements are selected.
    m &= (sum(selected[i] for i in range(n)) == count)

    # The selected elements sum to zero.
    m &= (sum(nums[i] * selected[i] for i in range(n)) == 0)

    # Satisfaction problem: no objective, only the selection is reported.
    return m, {"indices": selected}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
