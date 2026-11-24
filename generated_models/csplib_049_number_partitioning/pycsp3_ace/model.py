# csplib_049_number_partitioning: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_049_number_partitioning.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_049_number_partitioning.py csplib_049_number_partitioning.json

from pycsp3 import *


def create_model(instance):
    """Partition the numbers 1 to N into two sets A and B of the same size, with
    the same sum and the same sum of squares."""
    n_numbers = instance["n"]  # N, the numbers 1 to N are partitioned
    half = n_numbers // 2      # size of each set, taken as N even: the two sets together hold all N numbers

    # A[i] is the i-th number of set A.
    A = VarArray(size=half, dom=range(1, n_numbers + 1))
    # B[i] is the i-th number of set B.
    B = VarArray(size=half, dom=range(1, n_numbers + 1))

    satisfy(
        # Every number from 1 to N is in exactly one of the sets A and B.
        AllDifferent(A + B),
        # The numbers in A and in B have the same sum.
        Sum(A) == Sum(B),
        # The squares of the numbers in A and in B have the same sum.
        Sum(a * a for a in A) == Sum(b * b for b in B),
    )

    return {"A": A, "B": B}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
