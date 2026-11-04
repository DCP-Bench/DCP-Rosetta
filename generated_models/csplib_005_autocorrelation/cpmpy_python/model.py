# csplib_005_autocorrelation: a CPMpy model from DCP Rosetta.
# Download the `csplib_005_autocorrelation.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_005_autocorrelation.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_005_autocorrelation.py csplib_005_autocorrelation.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Low autocorrelation binary sequences: choose a sequence of n values, each +1 or -1,
    that minimises the sum of the squared periodic autocorrelations
    C_k = sum_i S_i * S_((i+k) mod n), for k = 1 to n-1."""
    n = instance["n"]  # the length of the sequence

    # plus[i] is true when the value S_i is +1 and false when it is -1. A boolean keeps the
    # value away from 0 without a "not equal to 0" constraint, and the products below
    # become linear.
    plus = cp.boolvar(shape=n, name="plus")

    # sequence[i] is the value S_i, either -1 or +1
    sequence = 2 * plus - 1

    model = cp.Model()

    # correlation[k-1] is the periodic autocorrelation C_k. Two values multiply to +1
    # when equal and to -1 when different, which is 2 * [equal] - 1.
    correlation = cp.intvar(-n, n, shape=n - 1, name="correlation")
    for k in range(1, n):
        shifted = plus[(np.arange(n) + k) % n]  # shifted[i] is plus[(i+k) mod n]
        model.add(correlation[k - 1] == cp.sum(2 * (plus == shifted) - 1))

    # energy is E, the sum of the squares of C_1 to C_(n-1).
    energy = cp.intvar(0, (n - 1) * n * n, name="energy")
    model.add(energy == cp.sum(correlation ** 2))

    # Minimise the energy.
    model.minimize(energy)

    return model, {"sequence": sequence}


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
