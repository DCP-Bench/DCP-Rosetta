# devils_word: a Python-MIP (Python) model from DCP Rosetta.
# Download the `devils_word.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python devils_word.py devils_word.json

import mip


def create_model(instance):
    """Given an array of integers, put a '+' or a '-' in front of each integer so
    that the signed integers add up to the given total. Output the array with its signs."""
    arr = instance["arr"]      # arr[i]: the integer that gets a sign
    total = instance["total"]  # the value the signed integers must add up to
    n = len(arr)               # the number of integers

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # plus[i] is 1 when integer i gets a '+' and 0 when it gets a '-'
    plus = [model.add_var(f"plus_{i}", var_type=mip.BINARY) for i in range(n)]
    # result[i] is integer i with its sign
    result = [
        model.add_var(f"result_{i}", lb=-abs(arr[i]), ub=abs(arr[i]), var_type=mip.INTEGER)
        for i in range(n)
    ]

    # Each integer gets one sign: result[i] is arr[i] for a '+' and -arr[i] for a '-'.
    for i in range(n):
        model.add_constr(result[i] == 2 * arr[i] * plus[i] - arr[i], f"sign_{i}")

    # The signed integers add up to the total.
    model.add_constr(mip.xsum(result) == total, "total")

    return model, {"result": result}


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
