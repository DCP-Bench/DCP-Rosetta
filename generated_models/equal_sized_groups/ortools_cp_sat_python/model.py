# equal_sized_groups: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `equal_sized_groups.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
# Then run it on the first instance (after `pip install ortools`):
#   python equal_sized_groups.py equal_sized_groups.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Divide a sorted list of n elements into k groups by choosing k-1 split points,
    keeping elements with the same value in the same group, with the groups as close
    in size to round(n/k) as possible."""
    a = instance["a"]                   # the sorted list of elements
    n_groups = instance["k"]            # the number of groups
    n_elements = len(a)                 # the number of elements
    group_size = round(n_elements / n_groups)  # the ideal size of a group

    model = cp_model.CpModel()

    # x[i] is the position of the last element of group i
    x = [model.new_int_var(1, n_elements, f"x_{i}") for i in range(n_groups - 1)]
    # sizes[i] is the number of elements in group i
    sizes = [model.new_int_var(1, n_elements, f"size_{i}") for i in range(n_groups)]
    # errors[i] is how far the size of group i is from the ideal size
    errors = [model.new_int_var(0, n_elements, f"error_{i}") for i in range(n_groups)]
    # total_error is the total gap from the ideal size across all groups
    total_error = model.new_int_var(0, n_elements, "total_error")

    # The first group ends at the first split point, the last group starts after the
    # last split point, and each group in between lies between two split points.
    model.add(sizes[0] == x[0])
    for i in range(1, n_groups - 1):
        model.add(sizes[i] == x[i] - x[i - 1])
    model.add(sizes[n_groups - 1] == n_elements - x[n_groups - 2])

    # Each error is the gap between one group size and the ideal size, and the total
    # error adds them up.
    for i in range(n_groups):
        model.add_abs_equality(errors[i], sizes[i] - group_size)
    model.add(total_error == sum(errors))

    # Elements with the same value stay together: no split point may fall between
    # two equal neighbours.
    for j in range(1, n_elements):
        if a[j - 1] == a[j]:
            for xi in x:
                model.add(xi != j)

    # Minimize the total error.
    model.minimize(total_error)

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
