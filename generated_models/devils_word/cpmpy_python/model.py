# devils_word: a CPMpy model from DCP Rosetta.
# Download the `devils_word.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python devils_word.py devils_word.json

import numpy as np
import cpmpy as cp


def create_model(instance):
    """Given an array of integers, insert '+' or '-' before each integer so that
    the signed integers sum to the given total."""
    arr = np.array(instance["arr"])  # arr[i]: the integer that gets a sign
    total = instance["total"]        # the sum the signed integers must reach
    n = len(arr)

    # plus[i] is true when arr[i] gets a '+', false when it gets a '-'
    plus = cp.boolvar(shape=n, name="plus")
    # result[i] is arr[i] with its chosen sign
    result = cp.intvar(-max(arr), max(arr), shape=n, name="result")

    model = cp.Model()
    # Each integer is added (plus is 1) or subtracted (plus is 0).
    model.add(result == arr * (2 * plus - 1))
    # The signed integers add up to the total.
    model.add(cp.sum(result) == total)

    return model, {"result": result}


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
