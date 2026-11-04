# csplib_084_hadamard_matrix: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_084_hadamard_matrix.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_084_hadamard_matrix.py csplib_084_hadamard_matrix.json

import z3


def create_model(instance):
    """Find two sequences a and b of odd length l, with entries -1 or +1, that each
    sum to 1 and whose periodic autocorrelations add up to -2 at every shift
    s = 1, ..., (l-1)/2 (a Legendre pair, which gives a Hadamard matrix)."""
    l = instance["l"]  # length of each sequence, an odd positive integer
    m = (l - 1) // 2   # number of shifts that are constrained

    # a[i] and b[i] are the entries of the two sequences
    a = [z3.Int(f"a_{i}") for i in range(l)]
    b = [z3.Int(f"b_{i}") for i in range(l)]

    def paf(seq, s):
        """Periodic autocorrelation of seq at shift s, with the index i + s taken modulo l."""
        # Each pair of entries contributes +1 when equal and -1 when different.
        return z3.Sum([z3.If(seq[i] == seq[(i + s) % l], 1, -1) for i in range(l)])

    solver = z3.Solver()

    # Every entry is -1 or +1.
    solver.add([z3.Or(v == -1, v == 1) for v in a + b])

    # Each sequence sums to 1.
    solver.add(z3.Sum(a) == 1)
    solver.add(z3.Sum(b) == 1)

    # At every shift s from 1 to m, the autocorrelations of a and b add up to -2.
    for s in range(1, m + 1):
        solver.add(paf(a, s) + paf(b, s) == -2)

    return solver, {"a": a, "b": b}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
