# devils_word: a SCIP (Python) model from DCP Rosetta.
# Download the `devils_word.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python devils_word.py devils_word.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Put a plus or a minus sign before each integer of a list so that the
    signed integers add up to a given total. Returns the model and its output
    result, the list of the signed integers."""
    arr = instance["arr"]      # arr[i]: the i-th integer of the list, which gets a sign
    total = instance["total"]  # the value the signed integers must add up to

    model = Model("devils_word")

    # plus[i] is 1 when the i-th integer gets a plus sign, and 0 when it gets a minus sign
    plus = [model.addVar(f"plus_{i}", vtype="B") for i in range(len(arr))]

    # The signed i-th integer is +arr[i] when plus[i] is 1 and -arr[i] when plus[i] is 0.
    # arr[i] is a constant, so this is linear in plus[i]: no indicator or big-M is needed.
    result = [a * (2 * p - 1) for a, p in zip(arr, plus)]

    # The signed integers add up to the total.
    model.addCons(quicksum(result) == total)

    return model, {"result": result}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
