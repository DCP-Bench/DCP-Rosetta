# equal_sized_groups: a Choco-solver (Python) model from DCP Rosetta.
# Download the `equal_sized_groups.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python equal_sized_groups.py equal_sized_groups.json

from pychoco.model import Model


def create_model(instance):
    """Split a sorted list of elements into k groups by choosing k - 1 split points,
    so that equal elements stay in one group and the group sizes are as close as
    possible to round(n / k). Minimise the total distance of the group sizes from round(n / k)."""
    a = instance["a"]  # the sorted elements to divide
    n_groups = instance["k"]  # the number of groups
    n_elements = len(a)  # the number of elements
    ideal_size = round(n_elements / n_groups)  # the group size to aim for

    # A split point at j sits after the j-th element. It may only sit between two
    # different values, so equal elements stay in one group.
    allowed_splits = [j for j in range(1, n_elements) if a[j - 1] != a[j]]

    model = Model()

    # x[p] is the p-th split point, the number of elements before it
    x = [model.intvar(allowed_splits, name=f"x_{p}") for p in range(n_groups - 1)]
    # s[i] is the number of elements in group i; every group has at least one
    s = [model.intvar(1, n_elements, name=f"s_{i}") for i in range(n_groups)]

    # The size of each group is the distance between its two split points.
    model.arithm(s[0], "=", x[0]).post()
    for i in range(1, n_groups - 1):
        model.arithm(x[i], "-", x[i - 1], "=", s[i]).post()
    model.arithm(s[n_groups - 1], "+", x[n_groups - 2], "=", n_elements).post()

    # signed_error[i] is negative when group i is too small
    signed_error = [model.intvar(-n_elements, n_elements, name=f"signed_error_{i}") for i in range(n_groups)]
    # error[i] is how far group i is from the ideal size
    error = [model.intvar(0, n_elements, name=f"error_{i}") for i in range(n_groups)]

    # Each signed error is the group size minus the ideal size, and each error is its absolute value.
    for i in range(n_groups):
        model.arithm(s[i], "-", ideal_size, "=", signed_error[i]).post()
        model.absolute(error[i], signed_error[i]).post()

    # total_error is the sum of the group errors, to minimise
    total_error = model.intvar(0, n_elements, name="total_error")
    model.sum(error, "=", total_error).post()

    return model, {"x": x}, {"objective": total_error, "maximize": False}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
