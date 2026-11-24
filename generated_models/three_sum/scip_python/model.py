# three_sum: a SCIP (Python) model from DCP Rosetta.
# Download the `three_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python three_sum.py three_sum.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Given a collection of integers, select exactly m of them whose sum is
    zero, and report which of the integers are selected."""
    nums = instance["nums"]  # the integers to choose from
    m = instance["m"]        # how many of the integers must be selected

    model = Model("three_sum")

    # x[i] is 1 when nums[i] is selected, and 0 when not
    x = [model.addVar(f"x_{i}", vtype="B") for i in range(len(nums))]

    # m is the number of elements to select, so exactly m of the x are 1.
    model.addCons(quicksum(x) == m)

    # The selected integers sum to zero.
    model.addCons(quicksum(v * xi for v, xi in zip(nums, x)) == 0)

    # No objective: any selection that meets both conditions is an answer.
    return model, {"indices": x}


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
