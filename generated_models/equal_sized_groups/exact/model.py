# equal_sized_groups: an Exact (Python) model from DCP Rosetta.
# Download the `equal_sized_groups.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python equal_sized_groups.py equal_sized_groups.json

from exact import Exact


def create_model(instance):
    """Divide a sorted list of n elements into k consecutive groups by choosing k - 1
    split points, keeping elements with the same value in the same group, so that the
    group sizes are as close as possible to round(n / k)."""
    a = instance["a"]                 # the sorted elements to divide
    n_groups = instance["k"]          # the number of groups
    n_elements = len(a)               # the number of elements
    ideal = round(n_elements / n_groups)  # the ideal size of a group

    solver = Exact()

    # Exact identifies its variables by name.
    # split[p] is the position of split point p: the first split[p] elements lie before it
    x = [f"split_{p}" for p in range(n_groups - 1)]
    for name in x:
        solver.addVariable(name, 1, n_elements - 1)

    # A split point can only fall between two elements that differ in value.
    allowed = [j for j in range(1, n_elements) if a[j - 1] != a[j]]
    # at[p][j] is 1 when split point p falls at position j, and 0 when not
    at = [[f"split_{p}_at_{j}" for j in allowed] for p in range(n_groups - 1)]
    for p in range(n_groups - 1):
        for name in at[p]:
            solver.addVariable(name, 0, 1)
        # Each split point falls at exactly one allowed position.
        solver.addConstraint([(1, name) for name in at[p]], True, 1, True, 1)
        solver.addConstraint([(j, name) for j, name in zip(allowed, at[p])] + [(-1, x[p])],
                             True, 0, True, 0)

    # Split points are in increasing order, so no group is empty.
    for p in range(1, n_groups - 1):
        solver.addConstraint([(1, x[p]), (-1, x[p - 1])], True, 1)

    # The first group ends at the first split point, and the last group runs from the last
    # split point to the end. Each group in between lies between two split points.
    sizes = []
    for i in range(n_groups):
        if i == 0:
            sizes.append(([(1, x[0])], 0))
        elif i < n_groups - 1:
            sizes.append(([(1, x[i]), (-1, x[i - 1])], 0))
        else:
            sizes.append(([(-1, x[n_groups - 2])], n_elements))

    # error[i] is how far the size of group i is from the ideal size, in either direction.
    error = [f"error_{i}" for i in range(n_groups)]
    for i in range(n_groups):
        solver.addVariable(error[i], 0, n_elements)
        terms, constant = sizes[i]
        # The error is at least the gap in each direction.
        solver.addConstraint([(1, error[i])] + [(-c, v) for c, v in terms], True, constant - ideal)
        solver.addConstraint([(1, error[i])] + terms, True, ideal - constant)

    # Minimise the total error over all groups.
    solver.setObjective([(1, name) for name in error], minimize=True)

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
