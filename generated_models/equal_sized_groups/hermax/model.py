# equal_sized_groups: a hermax (Python) model from DCP Rosetta.
# Download the `equal_sized_groups.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
# Then run it on the first instance (after `pip install hermax`):
#   python equal_sized_groups.py equal_sized_groups.json

from hermax.model import Model


def create_model(instance):
    """Split a sorted list of N elements into K consecutive groups by choosing K-1 break
    points, never between two equal values, so that the total deviation of the group sizes
    from round(N / K) is as small as possible."""
    a = instance["a"]      # a[i]: the value of element i of the sorted list (0-based)
    k = instance["k"]      # k: the number of groups
    n = len(a)             # n: the number of elements
    target = round(n / k)  # the ideal size of each group, round(N / K)

    m = Model()

    # x[i] is the 1-based index of the last element of group i (i = 0 .. K-2), the break points.
    # The last group ends at element N, so every break point lies between elements 1 and N-1.
    x = m.int_vector("x", k - 1, 1, n - 1)

    # Break points strictly increase, so every group has at least one element.
    for i in range(k - 2):
        m &= (x[i + 1] >= x[i] + 1)

    # Equal values must share a group: a break after element v (1-based) is only allowed
    # where a[v-1] and a[v] differ.
    for v in range(1, n):
        if a[v - 1] == a[v]:
            for i in range(k - 1):
                m &= (x[i] != v)

    # sizes[g] is the number of elements in group g. The first group starts at element 1,
    # the last group ends at element N, and each other group runs between two break points.
    sizes = []
    for g in range(k):
        s = m.int(f"size_{g}", 1, n)  # the number of elements in group g
        if g == 0:
            m &= (s == x[0])
        elif g == k - 1:
            m &= (s + x[k - 2] == n)
        else:
            m &= (s == x[g] - x[g - 1])
        sizes.append(s)

    # deviation[g] is the distance of group g's size from the target: it is at least the size
    # minus the target, and at least the target minus the size, so it equals the absolute difference
    # once the objective pushes it down.
    deviation = []
    for g in range(k):
        d = m.int(f"deviation_{g}", 0, n)  # |size of group g - round(N / K)|
        m &= (d >= sizes[g] - target)
        m &= (d >= target - sizes[g])
        deviation.append(d)

    # Minimise the total deviation of all group sizes from round(N / K).
    m.obj += sum(deviation)

    return m, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
