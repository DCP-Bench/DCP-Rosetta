# csplib_084_hadamard_matrix: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_084_hadamard_matrix.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_084_hadamard_matrix.py csplib_084_hadamard_matrix.json

from hermax.model import Model


def create_model(instance):
    """Hadamard matrix Legendre pairs (CSPLib 084).

    Find two sequences a[0..l-1] and b[0..l-1], each entry -1 or +1, such that
    both sequences sum to 1, and for every shift s = 1..m, where m = (l - 1) / 2,
    the periodic autocorrelation of a at shift s plus that of b at shift s is -2.
    The periodic autocorrelation PAF(A, s) is the sum over i of A[i] * A[(i + s) mod l].
    """
    l = instance["l"]  # l: the length of each sequence (an odd number)
    half = (l - 1) // 2  # m: the number of shifts constrained, s = 1..m

    model = Model()

    # a[i] is the i-th entry of sequence A, and b[i] of sequence B; each is -1 or +1
    a = model.int_vector("a", l, -1, 1)
    b = model.int_vector("b", l, -1, 1)
    for i in range(l):
        model &= a[i].forbid_value(0)  # entries are never 0
        model &= b[i].forbid_value(0)

    # Each sequence sums to 1. With l odd, that means (l + 1) / 2 entries are +1.
    model &= (sum(a[i] for i in range(l)) == 1)
    model &= (sum(b[i] for i in range(l)) == 1)

    def same_sign_flags(model, seq):
        # flags[(i, s)] is true when seq[i] and seq[(i + s) mod l] are equal,
        # so their product is +1; when they differ, the product is -1.
        flags = {}
        for s in range(1, half + 1):
            for i in range(l):
                same = model.bool()
                model &= (seq[i] == seq[(i + s) % l]).iff(same)
                flags[(i, s)] = same
        return flags

    same_a = same_sign_flags(model, a)
    same_b = same_sign_flags(model, b)

    # For each shift s: PAF(A, s) + PAF(B, s) = -2. Since each product is 2 * same - 1,
    # PAF(A, s) = 2 * (number of same-sign pairs) - l, which turns the condition into
    # (same-sign pairs of A) + (same-sign pairs of B) = l - 1.
    for s in range(1, half + 1):
        model &= (sum(same_a[(i, s)] for i in range(l))
                  + sum(same_b[(i, s)] for i in range(l)) == l - 1)

    return model, {"a": a, "b": b}

if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
