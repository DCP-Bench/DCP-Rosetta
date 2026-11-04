# clock_triplets: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
# Run it (after `pip install mip numpy`) with:
#   python clock_triplets.py

import mip


def create_model(instance):
    """Rearrange the numbers 1 to 12 on the face of a clock so that no triplet of
    adjacent numbers has a sum higher than 21, the smallest value the highest
    triplet sum can have."""
    n_numbers = 12  # the numbers on the clock face, 1 to 12
    max_sum = 21    # the highest allowed sum of three adjacent numbers

    model = mip.Model()

    # p[i][k] is 1 when position i of the clock face holds the number k + 1
    p = [[model.add_var(f"p_{i}_{k}", var_type=mip.BINARY) for k in range(n_numbers)] for i in range(n_numbers)]

    # x[i] is the number at position i of the clock face, going round the face
    x = [model.add_var(f"x_{i}", lb=1, ub=n_numbers, var_type=mip.INTEGER) for i in range(n_numbers)]

    # Each position holds exactly one number.
    for i in range(n_numbers):
        model += mip.xsum(p[i]) == 1

    # The number at position i is x[i].
    for i in range(n_numbers):
        model += x[i] == mip.xsum((k + 1) * p[i][k] for k in range(n_numbers))

    # Each number from 1 to 12 appears once on the clock.
    for k in range(n_numbers):
        model += mip.xsum(p[i][k] for i in range(n_numbers)) == 1

    # Every three adjacent numbers, wrapping round the face, sum to at most max_sum.
    for i in range(n_numbers):
        model += x[i] + x[(i + 1) % n_numbers] + x[(i + 2) % n_numbers] <= max_sum

    return model, {"x": x}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
