# csplib_024_langford: a CPMpy model from DCP Rosetta.
# Download the `csplib_024_langford.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_024_langford.py csplib_024_langford.json

import cpmpy as cp


def create_model(instance):
    """Arrange two copies of each number from 1 to k into one sequence of 2k numbers, so that the
    two 1's appear one number apart, the two 2's two numbers apart, ..., and the two k's k numbers
    apart."""
    k = instance["k"]  # the sequence holds two copies of each number from 1 to k

    # position[i - 1] and position[k + i - 1] are the places in the sequence of the two copies of
    # number i. The 2k places are all different, so the sequence is filled completely.
    position = cp.intvar(0, 2 * k - 1, shape=2 * k, name="position")

    # sol[p] is the number at place p of the sequence
    sol = cp.intvar(1, k, shape=2 * k, name="sol")

    model = cp.Model()

    # The two copies of a number never share a place, and no two numbers share one.
    model.add(cp.AllDifferent(position))

    for i in range(1, k + 1):
        # The second copy of i comes i numbers after the first (i + 1 places further on).
        model.add(position[i + k - 1] == position[i - 1] + i + 1)
        # Both copies of i stand at their places in the sequence.
        model.add(sol[position[i - 1]] == i)
        model.add(sol[position[k + i - 1]] == i)

    return model, {"sol": sol}


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
