# csplib_005_autocorrelation: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_005_autocorrelation.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_005_autocorrelation.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_005_autocorrelation.py csplib_005_autocorrelation.json

from pycsp3 import *


def create_model(instance):
    """Find a binary sequence of length n, each bit +1 or -1, that minimises the sum of the
    squares of its periodic (cyclic) autocorrelations. The k-th periodic autocorrelation is
    C_k = sum over i from 0 to n-1 of S_i * S_((i+k) mod n), and the energy to minimise is
    E = sum over k from 1 to n-1 of C_k^2."""
    n = instance["n"]  # the length of the sequence

    # sequence[i] is the bit S_i of the sequence, +1 or -1.
    sequence = VarArray(size=n, dom={-1, 1})

    # corr[k - 1] is the periodic autocorrelation C_k for shift k from 1 to n-1; it is a sum of n products of +1 and -1, so it lies between -n and n.
    corr = VarArray(size=n - 1, dom=range(-n, n + 1))

    # Each C_k is the sum of the products of each bit with the bit k places further on, wrapping around (periodic boundary).
    satisfy(
        corr[k - 1] == Sum(sequence[i] * sequence[(i + k) % n] for i in range(n))
        for k in range(1, n)
    )

    # Minimise the energy E, the sum of the squares of the autocorrelations C_1 to C_(n-1).
    minimize(Sum(c * c for c in corr))

    return {"sequence": sequence}


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
