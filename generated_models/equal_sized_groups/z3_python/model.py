# equal_sized_groups: a Z3 (Python) model from DCP Rosetta.
# Download the `equal_sized_groups.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python equal_sized_groups.py equal_sized_groups.json

import z3


def create_model(instance):
    """A sorted list of n elements is divided into k groups by choosing k - 1 break
    points between the elements. Elements with the same value stay in the same group.
    The groups are to be as close in size to round(n / k) as possible. Find the
    break points that minimise the total difference in size."""
    a = instance["a"]  # the sorted list of elements
    n_groups = instance["k"]  # the number of groups
    n_elements = len(a)  # the number of elements
    group_size = round(n_elements / n_groups)  # the ideal size of a group

    # Every number in the model is at most n_groups * n_elements, so this width holds them all.
    width = (n_groups * n_elements).bit_length() + 1

    # The whole number with this value, in that width.
    def const(value):
        return z3.BitVecVal(value, width)

    # how far the size of a group is from the ideal size
    def miss(size):
        return z3.If(
            z3.UGE(size, const(group_size)),
            size - const(group_size),
            const(group_size) - size,
        )

    # x[i] is the 1-based index of break point i, the last element of group i
    x = [z3.BitVec(f"x_{i}", width) for i in range(n_groups - 1)]

    # The conditions on the break points and the groups.
    solver = z3.Optimize()

    # Each break point is between the first and the last element.
    for xi in x:
        solver.add(z3.UGE(xi, const(1)), z3.ULE(xi, const(n_elements)))

    # Break points go in increasing order, so every group has at least one element.
    solver.add([z3.UGT(x[i], x[i - 1]) for i in range(1, n_groups - 1)])

    # The last break point is before the last element, so the last group has an element.
    solver.add(z3.ULT(x[n_groups - 2], const(n_elements)))

    # sizes[i] is the number of elements in group i. The first group runs up to the
    # first break point, a middle group runs between two break points, and the last
    # group runs from the last break point to the end.
    sizes = (
        [x[0]]
        + [x[i] - x[i - 1] for i in range(1, n_groups - 1)]
        + [const(n_elements) - x[n_groups - 2]]
    )

    # A break point falls only where the value changes, so equal values stay together.
    # allowed lists the 1-based positions j where element j and element j + 1 differ.
    allowed = [j for j in range(1, n_elements) if a[j - 1] != a[j]]
    solver.add([z3.Or([xi == const(j) for j in allowed]) for xi in x])

    # error is the total difference between the group sizes and the ideal size.
    error = z3.Sum([miss(s) for s in sizes])

    # The total error is at most n_elements.
    solver.add(z3.ULE(error, const(n_elements)))

    # Minimise the total error.
    solver.minimize(z3.BV2Int(error))

    return solver, {"x": [z3.BV2Int(xi) for xi in x]}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
