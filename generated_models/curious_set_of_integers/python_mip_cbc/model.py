# curious_set_of_integers: a Python-MIP (Python) model from DCP Rosetta.
# Download the `curious_set_of_integers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python curious_set_of_integers.py curious_set_of_integers.json

import math

import mip


def create_model(instance):
    """The integers 1, 3, 8 and 120 form a set in which the product of any two
    integers is one less than a perfect square. Find a fifth number (at least 0)
    that can be added to the set without destroying this property."""
    n = instance["n"]              # the number of integers in the set: the four given and the one to find
    max_val = instance["max_val"]  # the largest value the number to find may take
    given = [1, 3, 8, 120]         # the four integers of the set in the statement
    assert n == len(given) + 1

    model = mip.Model()

    # The fifth number, the one to find
    number = model.add_var("number", lb=0, ub=max_val, var_type=mip.INTEGER)

    # The largest square root needed for a given integer times the number, plus 1
    max_root = math.isqrt(max(given) * max_val + 1)

    # The product of the number and each given integer is one less than a square.
    for a in given:
        # choice[k] is 1 when k is the square root of a times the number, plus 1
        choice = [model.add_var(var_type=mip.BINARY) for k in range(max_root + 1)]
        model.add_constr(mip.xsum(choice) == 1)
        model.add_constr(mip.xsum(k * k * choice[k] for k in range(max_root + 1)) == a * number + 1)

    return model, {"number": number}


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
