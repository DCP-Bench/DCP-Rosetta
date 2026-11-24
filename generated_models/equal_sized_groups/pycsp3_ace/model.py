# equal_sized_groups: a PyCSP3 model from DCP Rosetta.
# Download the `equal_sized_groups.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python equal_sized_groups.py equal_sized_groups.json

from pycsp3 import *


def create_model(instance):
    """A sorted list of N elements is divided into K groups by choosing K - 1 break
    points between them. Equal values must stay in the same group, and each group holds
    at least one element. A break point is the number of elements before it. Find the
    break points that minimise the total error, the sum over the groups of the difference
    between the group's size and round(N / K)."""
    elements = instance["a"]  # the sorted list of elements
    n_groups = instance["k"]  # K, the number of groups
    n_elements = len(elements)  # N, the number of elements
    ideal_size = round(n_elements / n_groups)  # round(N / K), the size each group should have

    # A break point b (1 <= b < N) lies between elements b - 1 and b; it is allowed only
    # where these two values differ, so that equal values stay in one group.
    valid_breaks = [b for b in range(1, n_elements) if elements[b - 1] != elements[b]]

    # breaks[i] is the number of elements before the (i + 1)-th break point
    breaks = VarArray(size=n_groups - 1, dom=valid_breaks)

    # The first group starts before element 0 and the last group ends after element N - 1,
    # so the bounds of the groups are 0, the break points and N.
    bounds = [0, *breaks, n_elements]

    # Each group holds at least one element: the break points are strictly increasing.
    satisfy(Increasing(breaks, strict=True))

    # The total error is minimised: the sum over the groups of the difference between the
    # size of the group (the gap between consecutive bounds) and the ideal size.
    minimize(Sum(abs(bounds[g + 1] - bounds[g] - ideal_size) for g in range(n_groups)))

    # The output x is the array of break points.
    return {"x": breaks}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
