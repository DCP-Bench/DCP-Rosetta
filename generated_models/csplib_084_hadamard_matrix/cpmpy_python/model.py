# csplib_084_hadamard_matrix: a CPMpy model from DCP Rosetta.
# Download the `csplib_084_hadamard_matrix.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_084_hadamard_matrix.py csplib_084_hadamard_matrix.json

import cpmpy as cp


def create_model(instance):
    """Find two sequences a and b of odd length l, with entries -1 or +1, that each
    sum to 1 and whose periodic autocorrelations add up to -2 at every shift
    s = 1, ..., (l-1)/2 (a Legendre pair, which gives a Hadamard matrix)."""
    l = instance["l"]  # length of each sequence, an odd positive integer
    m = (l - 1) // 2   # number of shifts that are constrained

    # a[i] and b[i] are the entries of the two sequences. They are declared over
    # -1..1 and the value 0 is excluded below.
    a = cp.intvar(-1, 1, shape=l, name="a")
    b = cp.intvar(-1, 1, shape=l, name="b")

    def paf(seq, s):
        """Periodic autocorrelation of seq at shift s, with the index i + s taken modulo l."""
        return cp.sum([seq[i] * seq[(i + s) % l] for i in range(l)])

    model = cp.Model()

    # Every entry is -1 or +1.
    model.add(a != 0)
    model.add(b != 0)

    # Each sequence sums to 1.
    model.add(cp.sum(a) == 1)
    model.add(cp.sum(b) == 1)

    # At every shift the two periodic autocorrelations add up to -2.
    for s in range(1, m + 1):
        model.add(paf(a, s) + paf(b, s) == -2)

    return model, {"a": a, "b": b}


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
