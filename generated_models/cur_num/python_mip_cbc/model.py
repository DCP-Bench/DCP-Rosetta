# cur_num: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
# Run it (after `pip install mip numpy`) with:
#   python cur_num.py

import math

import mip


def create_model(instance):
    """The number 48 is peculiar: adding 1 to it gives a square number, and adding 1
    to its half gives a square number too. Find another number between 1 and 10000
    with this peculiarity."""
    top = 10000  # the largest number considered

    model = mip.Model()

    # The peculiar number, and half of it
    peculiar = model.add_var("peculiar", lb=1, ub=top, var_type=mip.INTEGER)
    half = model.add_var("half", lb=0, ub=top // 2, var_type=mip.INTEGER)

    # The number has a half, so it is even and half is its half.
    model.add_constr(peculiar == 2 * half)

    # root[k] is 1 when k is the square root of the number plus 1
    max_root = math.isqrt(top + 1)
    root = [model.add_var(f"root_{k}", var_type=mip.BINARY) for k in range(max_root + 1)]

    # Adding 1 to the number gives a square number.
    model.add_constr(mip.xsum(root) == 1)
    model.add_constr(mip.xsum(k * k * root[k] for k in range(max_root + 1)) == peculiar + 1)

    # half_root[k] is 1 when k is the square root of half of the number plus 1
    max_half_root = math.isqrt(top // 2 + 1)
    half_root = [model.add_var(f"half_root_{k}", var_type=mip.BINARY) for k in range(max_half_root + 1)]

    # Adding 1 to half of the number also gives a square number.
    model.add_constr(mip.xsum(half_root) == 1)
    model.add_constr(mip.xsum(k * k * half_root[k] for k in range(max_half_root + 1)) == half + 1)

    # above_48 is 1 when the number is larger than 48, and 0 when it is smaller
    above_48 = model.add_var("above_48", var_type=mip.BINARY)

    # The number is not 48, the example in the statement.
    model.add_constr(peculiar <= 47 + (top - 47) * above_48)
    model.add_constr(peculiar >= 49 * above_48)

    return model, {"peculiar": peculiar}


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
