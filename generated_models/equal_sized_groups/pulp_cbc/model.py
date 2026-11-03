# equal_sized_groups: a PuLP (Python) model from DCP Rosetta.
# Download the `equal_sized_groups.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python equal_sized_groups.py equal_sized_groups.json

import pulp


def create_model(instance):
    """Divide a sorted list of n elements into k groups by choosing k - 1 split points,
    keeping elements with the same value in the same group, with the groups as close
    in size to round(n / k) as possible. The output is the split points."""
    a = instance["a"]          # the sorted list of elements
    n_groups = instance["k"]   # the number of groups
    n_elements = len(a)        # the number of elements
    group_size = round(n_elements / n_groups)  # the ideal size of a group

    problem = pulp.LpProblem("groups", pulp.LpMinimize)

    # x[i] is the 1-based index of the last element of group i, the i-th split point
    x = [pulp.LpVariable(f"x_{i}", 1, n_elements, cat="Integer") for i in range(n_groups - 1)]
    # sizes[i] is the number of elements in group i
    sizes = [pulp.LpVariable(f"size_{i}", 1, n_elements, cat="Integer") for i in range(n_groups)]

    # The first group ends at the first split point, each middle group runs from one
    # split point to the next, and the last group runs from the last split point to the end.
    problem += sizes[0] == x[0]
    for i in range(1, n_groups - 1):
        problem += sizes[i] == x[i] - x[i - 1]
    problem += sizes[n_groups - 1] == n_elements - x[n_groups - 2]

    # errors[i] is how far the size of group i is from the ideal size
    errors = []
    for i in range(n_groups):
        error = pulp.LpVariable(f"error_{i}", 0, n_elements, cat="Integer")
        # Each error is at least the size minus the ideal size, and at least the ideal size
        # minus the size. Minimized, it equals the gap in either direction.
        problem += error >= sizes[i] - group_size
        problem += error >= group_size - sizes[i]
        errors.append(error)

    # Equal values stay together: no split point falls between two equal neighbours.
    for j in range(1, n_elements):
        if a[j - 1] != a[j]:
            continue
        for p in range(n_groups - 1):
            # below is 1 when split point p lies before element j, and 0 when it lies after it
            below = pulp.LpVariable(f"below_{j}_{p}", cat="Binary")
            problem += x[p] <= j - 1 + n_elements * (1 - below)
            problem += x[p] >= j + 1 - n_elements * below

    # Minimize the total gap from the ideal size over all groups.
    problem += pulp.lpSum(errors)

    return problem, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
