# csplib_084_hadamard_matrix: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_084_hadamard_matrix.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_084_hadamard_matrix.py csplib_084_hadamard_matrix.json

from pycsp3 import *


def create_model(instance):
    """For an odd positive integer l, with m = (l - 1) / 2, find two sequences A = [a_1, ..., a_l] and
    B = [b_1, ..., b_l] with values -1 or +1, such that for every s = 1, ..., m the periodic
    autocorrelations satisfy PAF(A, s) + PAF(B, s) = -2, where PAF(A, s) is the sum of a_i a_{i+s} over
    i = 1, ..., l and i + s wraps around modulo l; and the entries of A sum to 1, as do those of B."""
    # l: the length of each sequence, an odd number.
    length = instance["l"]

    # n_shifts: m = (l - 1) / 2, the number of shifts s and of quadratic constraints.
    n_shifts = (length - 1) // 2

    # a[i] is the entry a_{i+1} of sequence A, -1 or +1.
    a = VarArray(size=length, dom={-1, 1})
    # b[i] is the entry b_{i+1} of sequence B, -1 or +1.
    b = VarArray(size=length, dom={-1, 1})

    # The required sum of the two periodic autocorrelations at each shift, from the statement.
    paf_sum = -2

    satisfy(
        # For each shift s = 1 .. m, PAF(A, s) + PAF(B, s) = -2; the index i + s wraps around modulo l
        # (0-based, so a[(i + s) % length] is a_{i+s} of the statement).
        [
            Sum(a[i] * a[(i + s) % length] + b[i] * b[(i + s) % length] for i in range(length)) == paf_sum
            for s in range(1, n_shifts + 1)
        ],
        # The entries of A sum to 1.
        Sum(a) == 1,
        # The entries of B sum to 1.
        Sum(b) == 1,
    )

    return {"a": a, "b": b}


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
