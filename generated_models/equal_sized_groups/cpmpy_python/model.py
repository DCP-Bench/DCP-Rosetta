# equal_sized_groups: a CPMpy model from DCP Rosetta.
# Download the `equal_sized_groups.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python equal_sized_groups.py equal_sized_groups.json

import cpmpy as cp


def create_model(instance):
    """Divide a sorted list of n elements into k groups by choosing k-1 split points,
    keeping elements with the same value in the same group, with the groups as close
    in size to round(n/k) as possible."""
    a = instance["a"]  # the sorted list of elements
    k = instance["k"]  # the number of groups
    n = len(a)
    group_size = round(n / k)  # the ideal size of a group

    # x[i] is the 1-based index of split point i: the last element of group i
    x = cp.intvar(1, n, shape=k - 1, name="x")
    # sizes[i] is the number of elements in group i
    sizes = cp.intvar(1, n, shape=k, name="sizes")
    # error is the total difference between the group sizes and the ideal size
    error = cp.intvar(0, n, name="error")

    model = cp.Model()

    # The first group ends at the first split point, the last group starts after the
    # last split point, and each group in between lies between two split points.
    model.add(sizes[0] == x[0])
    for i in range(1, k - 1):
        model.add(sizes[i] == x[i] - x[i - 1])
    model.add(sizes[k - 1] == n - x[k - 2])

    # Elements with the same value stay together: no split point lies between
    # element j-1 and element j when they are equal. This compares instance data,
    # so only the real restrictions are posted.
    for j in range(1, n):
        if a[j - 1] == a[j]:
            model.add(x != j)

    # The total error is how far the group sizes are from the ideal size.
    model.add(error == cp.sum(cp.abs(sizes - group_size)))

    # Minimize the total error.
    model.minimize(error)

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
