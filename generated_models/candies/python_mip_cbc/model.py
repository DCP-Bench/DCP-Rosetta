# candies: a Python-MIP (Python) model from DCP Rosetta.
# Download the `candies.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python candies.py candies.json

import mip


def create_model(instance):
    """Alice, a kindergarten teacher, gives candies to the children sitting in a line, each with a
    rating. Every child gets at least 1 candy, and of two neighbours the one with the higher
    rating gets more candies. Minimize the total number of candies."""
    ratings = instance["ratings"]  # ratings[i]: the rating of the child at position i
    n = len(ratings)               # the number of children

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[i] is the number of candies the child at position i gets. In an optimal distribution no
    # child gets more candies than there are children, so n is an upper bound.
    x = [model.add_var(f"x_{i}", lb=1, ub=n, var_type=mip.INTEGER) for i in range(n)]

    # z is the total number of candies handed out
    z = model.add_var("z", lb=0, ub=n * n, var_type=mip.INTEGER)

    # The total is the sum of the candies of all the children.
    model += z == mip.xsum(x)

    # Of two neighbours, the child with the higher rating gets more candies. Equal ratings
    # give no constraint.
    for i in range(n - 1):
        if ratings[i] > ratings[i + 1]:
            model += x[i] >= x[i + 1] + 1
        elif ratings[i] < ratings[i + 1]:
            model += x[i + 1] >= x[i] + 1

    # Minimize the total number of candies.
    model.objective = z

    return model, {"x": x, "z": z}


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
