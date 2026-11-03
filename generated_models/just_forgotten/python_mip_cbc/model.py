# just_forgotten: a Python-MIP (Python) model from DCP Rosetta.
# Download the `just_forgotten.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python just_forgotten.py just_forgotten.json

import mip


def create_model(instance):
    """Find Joe's bank account number. It has each digit from 0 to n-1 once. In each set of
    digits Joe tried, a given number of digits are in their correct position."""
    sets = instance["sets"]                       # sets[k][i]: digit i of the k-th set of digits Joe tried
    num_correct = instance["num_correct_digits"]  # the number of digits in their correct position in each set
    n_digits = len(sets[0])                       # the number of digits in the account number

    model = mip.Model(solver_name="CBC")

    # x[i] is digit i of the account number, a digit from 0 to n_digits - 1.
    x = [model.add_var(f"x_{i}", lb=0, ub=n_digits - 1, var_type=mip.INTEGER) for i in range(n_digits)]

    # at[i][v] is 1 when digit v is in position i of the account number, and 0 when not.
    at = [
        [model.add_var(f"at_{i}_{v}", var_type=mip.BINARY) for v in range(n_digits)]
        for i in range(n_digits)
    ]

    # Each position holds exactly one digit, and x[i] is that digit.
    for i in range(n_digits):
        model.add_constr(mip.xsum(at[i][v] for v in range(n_digits)) == 1)
        model.add_constr(x[i] == mip.xsum(v * at[i][v] for v in range(n_digits)))

    # Each digit from 0 to n_digits - 1 is used exactly once.
    for v in range(n_digits):
        model.add_constr(mip.xsum(at[i][v] for i in range(n_digits)) == 1)

    # In each set, exactly num_correct digits are in the same position as in the account number.
    for s in sets:
        model.add_constr(mip.xsum(at[i][s[i]] for i in range(n_digits)) == num_correct)

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
