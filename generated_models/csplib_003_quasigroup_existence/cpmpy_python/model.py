# csplib_003_quasigroup_existence: a CPMpy model from DCP Rosetta.
# Download the `csplib_003_quasigroup_existence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_003_quasigroup_existence.py csplib_003_quasigroup_existence.json

import cpmpy as cp


def create_model(instance):
    """QG3.m quasigroup existence: find an order m quasigroup, a Latin square of size
    m with every element once in each row and column, such that (a*b)*(b*a) = a."""
    m = instance["m"]  # the order of the quasigroup

    # quasigroup[a, b] is the product a*b, an element from 0 to m-1
    quasigroup = cp.intvar(0, m - 1, shape=(m, m), name="quasigroup")

    model = cp.Model()

    # Latin square: each element occurs once in every row and every column.
    for i in range(m):
        model.add(cp.AllDifferent(quasigroup[i, :]))
        model.add(cp.AllDifferent(quasigroup[:, i]))

    # QG3.m: (a*b)*(b*a) = a for all a and b.
    for a in range(m):
        for b in range(m):
            model.add(quasigroup[quasigroup[a, b], quasigroup[b, a]] == a)

    return model, {"quasigroup": quasigroup}


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
