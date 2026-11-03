# csplib_049_number_partitioning: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_049_number_partitioning.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_049_number_partitioning.py csplib_049_number_partitioning.json

from hermax.model import Model, sum_expr


def create_model(instance):
    """Split the numbers 1..N into two sets A and B of equal size such that A and B
    have the same sum and the same sum of squares. Output the members of A and of B,
    each in increasing order."""
    N = instance["n"]          # n: the numbers to split are 1..n
    h = N // 2                 # A and B must have the same cardinality, so each holds half of them

    m = Model()

    # A[k] is the k-th smallest number in A, and B[k] the k-th smallest number in B
    A = m.int_vector("A", h, 1, N)
    B = m.int_vector("B", N - h, 1, N)

    # Every number from 1 to N is used exactly once, in A or in B.
    m &= m.vector([A[k] for k in range(h)] + [B[k] for k in range(N - h)]).all_different()
    # Listing each set in increasing order gives one output per partition.
    m &= A.increasing()
    m &= B.increasing()

    # The sum of the numbers in A equals the sum of the numbers in B.
    m &= (sum(A) == sum(B))

    # The square of a number v: a step function of the number, equal to v*v.
    def square(x):
        return x.piecewise(base_value=1, steps={v: v * v for v in range(2, N + 1)})

    # The sum of squares of the numbers in A equals the sum of squares of the numbers in B.
    m &= (sum_expr(square(A[k]) for k in range(h)) == sum_expr(square(B[k]) for k in range(N - h)))

    return m, {"A": A, "B": B}


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
