# csplib_084_hadamard_matrix: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_084_hadamard_matrix.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_084_hadamard_matrix.py csplib_084_hadamard_matrix.json

import cvc5.pythonic as c5


def sign(p):
    # The entry of a sequence: +1 when p is true, -1 otherwise.
    return c5.If(p, 1, -1)


def paf(plus, s, l):
    # The periodic autocorrelation of a sequence at shift s: the sum of the products of
    # each entry with the entry s places later, wrapping around. A product is +1 when
    # the two entries are equal and -1 when they differ.
    return c5.Sum([c5.If(plus[i] == plus[(i + s) % l], 1, -1) for i in range(l)])


def create_model(instance):
    """Find two sequences a and b of odd length l, with entries -1 or +1, that each
    sum to 1 and whose periodic autocorrelations add up to -2 at every shift
    s = 1, ..., (l-1)/2 (a Legendre pair, which gives a Hadamard matrix)."""
    l = instance["l"]         # length of each sequence, an odd positive integer
    n_shifts = (l - 1) // 2   # number of shifts that are constrained

    # plus_a[i] is true when entry i of a is +1, and plus_b[i] likewise for b
    plus_a = [c5.Bool(f"plus_a_{i}") for i in range(l)]
    plus_b = [c5.Bool(f"plus_b_{i}") for i in range(l)]

    solver = c5.Solver()

    # At every shift, the autocorrelations of a and b add up to -2.
    solver.add([paf(plus_a, s, l) + paf(plus_b, s, l) == -2 for s in range(1, n_shifts + 1)])

    # Each sequence sums to 1.
    solver.add(
        c5.Sum([sign(p) for p in plus_a]) == 1,
        c5.Sum([sign(p) for p in plus_b]) == 1,
    )

    a = [sign(p) for p in plus_a]
    b = [sign(p) for p in plus_b]
    return solver, {"a": a, "b": b}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
