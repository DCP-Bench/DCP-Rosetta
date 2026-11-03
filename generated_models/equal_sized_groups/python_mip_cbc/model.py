# equal_sized_groups: a Python-MIP (Python) model from DCP Rosetta.
# Download the `equal_sized_groups.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python equal_sized_groups.py equal_sized_groups.json

import mip


def create_model(instance):
    """Divide a sorted list of elements into k groups by choosing k - 1 break points
    between them. Elements with the same value stay in the same group. The groups
    should be as close in size to round(n / k) as possible, where n is the number of
    elements."""
    a = instance["a"]  # a[j] is the value of element j + 1, elements numbered from 1
    k = instance["k"]  # the number of groups
    n = len(a)  # the number of elements
    ideal_size = round(n / k)  # the size each group should have

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Positions where a break point may fall: after element p, and only where the next value is different.
    valid = [p for p in range(1, n) if a[p - 1] != a[p]]

    # x[i] is the element after which break point i falls.
    # z[i, p] is 1 when break point i falls after element p.
    x = []
    z = {}
    for i in range(k - 1):
        xi = model.add_var(f"x_{i}", lb=1, ub=n - 1, var_type=mip.INTEGER)
        x.append(xi)
        for p in valid:
            z[i, p] = model.add_var(f"z_{i}_{p}", var_type=mip.BINARY)
        # Each break point falls at exactly one allowed position.
        model.add_constr(mip.xsum(z[i, p] for p in valid) == 1)
        # x[i] is that position.
        model.add_constr(xi == mip.xsum(p * z[i, p] for p in valid))

    # Two break points do not fall after the same element.
    for p in valid:
        model.add_constr(mip.xsum(z[i, p] for i in range(k - 1)) <= 1)

    # The break points come in order from left to right.
    for i in range(k - 2):
        model.add_constr(x[i] + 1 <= x[i + 1])

    # bounds lists 0, the break points and n: group j holds the elements from bounds[j] + 1 to bounds[j + 1].
    bounds = [0] + x + [n]
    # errors[j] is the gap between the size of group j and the ideal size, in either direction.
    errors = []
    for j in range(k):
        group_size = bounds[j + 1] - bounds[j]
        error = model.add_var(f"e_{j}", lb=0, ub=n, var_type=mip.INTEGER)
        # The error is at least the size minus the ideal size, and at least the ideal size minus the size.
        model.add_constr(error >= group_size - ideal_size)
        model.add_constr(error >= ideal_size - group_size)
        errors.append(error)

    # The total error over all groups is minimised.
    model.objective = mip.xsum(errors)

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
