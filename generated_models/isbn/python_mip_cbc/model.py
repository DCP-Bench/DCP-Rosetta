# isbn: a Python-MIP (Python) model from DCP Rosetta.
# Download the `isbn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python isbn.py isbn.json

import mip


def create_model(instance):
    """Fill in the unknown digits (-1) of a 13-digit ISBN so that it is valid. An ISBN-13
    starts with 978 or 979. Its last digit is a check digit: with the digits weighted 1 and 3
    alternately from the left, the weighted sum of all 13 digits is a multiple of 10."""
    isbn_init = instance["isbn_init"]  # isbn_init[i]: digit i of the ISBN, or -1 when unknown
    n_digits = len(isbn_init)          # the number of digits in the ISBN

    model = mip.Model(solver_name="CBC")

    # The first three digits are 9, 7, and 8 or 9, since the ISBN starts with 978 or 979.
    prefix_low = [9, 7, 8]   # the least value of digits 0, 1 and 2
    prefix_high = [9, 7, 9]  # the greatest value of digits 0, 1 and 2

    # isbn[i] is digit i of the ISBN. A given digit is fixed, and an unknown digit is 0 to 9.
    isbn = []
    for i, given in enumerate(isbn_init):
        low, high = (given, given) if given >= 0 else (0, 9)
        if i < len(prefix_low):
            low, high = max(low, prefix_low[i]), min(high, prefix_high[i])
        isbn.append(model.add_var(f"d{i}", lb=low, ub=high, var_type=mip.INTEGER))

    # Digit i counts 1 when i is even and 3 when i is odd.
    weights = [1 if i % 2 == 0 else 3 for i in range(n_digits)]

    # k: the weighted sum of the digits divided by 10.
    k = model.add_var("k", lb=0, ub=9 * sum(weights) // 10, var_type=mip.INTEGER)

    # The check digit makes the weighted sum of all 13 digits a multiple of 10.
    model += mip.xsum(w * d for w, d in zip(weights, isbn)) == 10 * k

    return model, {"isbn": isbn}


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
