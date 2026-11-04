# four_numbers: a Python-MIP (Python) model from DCP Rosetta.
# Download the `four_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_numbers.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python four_numbers.py four_numbers.json

import mip


def create_model(instance):
    """Given up to four distinct integers between 1 and 10, find three integers between 1 and 10
    such that every given number is the sum of some of the three."""
    numbers = instance["numbers"]  # the given numbers, each of which must be a sum of some of the three
    n_numbers = len(numbers)       # how many given numbers there are
    top = 10                       # the largest value of each integer to find

    model = mip.Model(solver_name="CBC")

    # x[j] is the j-th of the three integers to find, between 1 and top.
    x = [model.add_var(f"x_{j}", lb=1, ub=top, var_type=mip.INTEGER) for j in range(3)]

    # The seven non-empty subsets of the three integers, each given as the positions of its integers.
    subsets = [[j for j in range(3) if (s >> j) & 1] for s in range(1, 8)]
    # The largest possible subset sum: all three integers at the top value.
    largest_sum = 3 * top

    for k in range(n_numbers):
        # z[s] is 1 when subset s is the one that adds up to numbers[k].
        z = [model.add_var(f"z_{k}_{s}", var_type=mip.BINARY) for s in range(len(subsets))]
        # w[s] is the sum of subset s when it is the one that adds up to numbers[k], and 0 otherwise.
        w = [model.add_var(f"w_{k}_{s}", lb=0, ub=largest_sum, var_type=mip.INTEGER)
             for s in range(len(subsets))]

        # Exactly one subset adds up to the given number.
        model += mip.xsum(z) == 1

        for s, members in enumerate(subsets):
            total = mip.xsum(x[j] for j in members)  # the sum of the integers in subset s
            # w[s] equals that sum when subset s is chosen, and 0 otherwise.
            model += w[s] <= total
            model += w[s] <= largest_sum * z[s]
            model += w[s] >= total - largest_sum * (1 - z[s])

        # The chosen subset adds up to the given number.
        model += mip.xsum(w) == numbers[k]

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
