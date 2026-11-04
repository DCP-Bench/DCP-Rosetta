# dudeney_numbers: a Python-MIP (Python) model from DCP Rosetta.
# Download the `dudeney_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python dudeney_numbers.py dudeney_numbers.json

import mip


def create_model(instance):
    """A Dudeney number is a positive integer that is a perfect cube such that
    the sum of its digits is equal to the cube root of the number. Find such a
    number that is larger than 1."""
    n = instance["n"]  # the most digits the number may have

    max_number = 10 ** n - 1  # the largest number with at most n digits

    # the largest cube root whose cube is at most max_number
    max_root = 1
    while (max_root + 1) ** 3 <= max_number:
        max_root += 1

    model = mip.Model(solver_name="CBC")

    # choose[k - 1] is 1 when k is the cube root of the number, for k from 1 to max_root
    choose = [model.add_var(f"c_{k}", var_type=mip.BINARY) for k in range(1, max_root + 1)]
    # root is the cube root of the number
    root = model.add_var("root", lb=1, ub=max_root, var_type=mip.INTEGER)
    # number is the Dudeney number, larger than 1 and with at most n digits
    number = model.add_var("number", lb=2, ub=max_number, var_type=mip.INTEGER)
    # digits[i] is the digit in place 10 ** i of the number, counting from the units
    digits = [model.add_var(f"d_{i}", lb=0, ub=9, var_type=mip.INTEGER) for i in range(n)]

    # Exactly one cube root is chosen.
    model += mip.xsum(choose) == 1

    # The cube root is the one chosen.
    model += root == mip.xsum(k * choose[k - 1] for k in range(1, max_root + 1))

    # The number is the cube of its cube root.
    model += number == mip.xsum(k ** 3 * choose[k - 1] for k in range(1, max_root + 1))

    # The digits written out make the number.
    model += number == mip.xsum(10 ** i * digits[i] for i in range(n))

    # The digits sum to the cube root.
    model += mip.xsum(digits) == root

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
