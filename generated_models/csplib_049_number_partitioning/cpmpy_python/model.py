# csplib_049_number_partitioning: a CPMpy model from DCP Rosetta.
# Download the `csplib_049_number_partitioning.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_049_number_partitioning.py csplib_049_number_partitioning.json

import cpmpy as cp


def create_model(instance):
    """Partition the numbers 1..n into two sets A and B of the same size, with
    the same sum and the same sum of squares."""
    n = instance["n"]  # the numbers 1..n are partitioned
    half = n // 2      # the size of each of the two sets

    # a[i] is the i-th number of set A
    a = cp.intvar(1, n, shape=half, name="a")
    # b[i] is the i-th number of set B
    b = cp.intvar(1, n, shape=half, name="b")

    model = cp.Model()
    # Every number appears once, in A or in B (the two sets have the same size, half each).
    model.add(cp.AllDifferent(cp.cpm_array(list(a) + list(b))))
    # A and B have the same sum.
    model.add(cp.sum(a) == cp.sum(b))
    # A and B have the same sum of squares.
    model.add(cp.sum(a ** 2) == cp.sum(b ** 2))

    return model, {"A": a, "B": b}


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
