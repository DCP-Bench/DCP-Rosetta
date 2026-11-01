# autoref: a CPMpy model from DCP Rosetta.
# Download the `autoref.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python autoref.py autoref.json

import cpmpy as cp


def create_model(instance):
    """Find a series s[0..n+1] in which every integer i from 0 to n occurs exactly
    s[i] times, and whose last element s[n+1] equals m."""
    n = instance["n"]  # the series has n + 2 elements, and counts the values 0 to n
    m = instance["m"]  # the required value of the last element

    # s[k] is the k-th element of the series; values lie between 0 and n
    s = cp.intvar(0, n, shape=n + 2, name="s")

    model = cp.Model()
    # The last element is m.
    model.add(s[n + 1] == m)
    # The value i occurs exactly s[i] times in the series, for every i from 0 to n.
    for i in range(n + 1):
        model.add(cp.Count(s, i) == s[i])

    return model, {"s": s}


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
