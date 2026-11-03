# bowls_and_oranges: a Python-MIP (Python) model from DCP Rosetta.
# Download the `bowls_and_oranges.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python bowls_and_oranges.py bowls_and_oranges.json

import mip


def create_model(instance):
    """Place all the oranges in the bowls, which stand in a line one metre apart and are
    numbered from 1. No bowl holds more than one orange, and no three oranges sit in bowls
    at equal distances from each other. The result gives the bowl of each orange."""
    n_bowls = instance["n"]    # the number of bowls
    n_oranges = instance["m"]  # the number of oranges

    model = mip.Model(solver_name="CBC")

    # in_bowl[k][j] is 1 when orange k is in bowl j + 1, and 0 when not
    in_bowl = [[model.add_var(f"in_bowl_{k}_{j}", var_type=mip.BINARY)
                for j in range(n_bowls)]
               for k in range(n_oranges)]
    # x[k] is the number of the bowl that orange k is in
    x = [model.add_var(f"x_{k}", lb=1, ub=n_bowls, var_type=mip.INTEGER)
         for k in range(n_oranges)]
    # occ[j] is the number of oranges in bowl j + 1
    occ = [mip.xsum(in_bowl[k][j] for k in range(n_oranges)) for j in range(n_bowls)]

    # Each orange is in exactly one bowl.
    for k in range(n_oranges):
        model += mip.xsum(in_bowl[k]) == 1

    # The bowl number of orange k is the bowl it is in.
    for k in range(n_oranges):
        model += x[k] == mip.xsum((j + 1) * in_bowl[k][j] for j in range(n_bowls))

    # No bowl holds more than one orange.
    for j in range(n_bowls):
        model += occ[j] <= 1

    # Orange k lies in an earlier bowl than orange k + 1.
    for k in range(n_oranges - 1):
        model += x[k] + 1 <= x[k + 1]

    # For any three bowls evenly spaced along the line, at most two of them hold an orange.
    for first in range(n_bowls):
        for gap in range(1, n_bowls):
            if first + 2 * gap > n_bowls - 1:
                break
            model += occ[first] + occ[first + gap] + occ[first + 2 * gap] <= 2

    return model, {"x": x}


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
