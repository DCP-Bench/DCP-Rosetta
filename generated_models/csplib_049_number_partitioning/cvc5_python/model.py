# csplib_049_number_partitioning: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_049_number_partitioning.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_049_number_partitioning.py csplib_049_number_partitioning.json

import cvc5.pythonic as c5


def create_model(instance):
    """Partition the numbers 1..n into two sets A and B of the same size, with
    the same sum and the same sum of squares."""
    n = instance["n"]                         # the numbers 1..n are partitioned
    set_size = n // 2                         # the size of each set
    total = n * (n + 1) // 2                  # the sum of the numbers 1..n
    total_sq = n * (n + 1) * (2 * n + 1) // 6  # the sum of the squares of the numbers 1..n

    # a[i] is the i-th number of set A, and b[i] the i-th number of set B
    a = [c5.Int(f"A_{i}") for i in range(set_size)]
    b = [c5.Int(f"B_{i}") for i in range(set_size)]

    # The numbers 1 to n, each a candidate for either set
    numbers = range(1, n + 1)

    solver = c5.Solver()

    # Each number is from 1 to n.
    solver.add([x >= 1 for x in a + b] + [x <= n for x in a + b])

    # Each set is listed in increasing order.
    solver.add([s[i] < s[i + 1] for s in (a, b) for i in range(set_size - 1)])

    # in_a[j - 1] is true when the number j is in set A, and in_b[j - 1] when it is in set B.
    in_a = [c5.Or([x == j for x in a]) for j in numbers]
    in_b = [c5.Or([x == j for x in b]) for j in numbers]

    # Every number is in exactly one of the two sets.
    solver.add([c5.And(c5.Or(ia, ib), c5.Not(c5.And(ia, ib))) for ia, ib in zip(in_a, in_b)])

    # A and B have the same number of elements.
    solver.add(c5.Sum([c5.If(ia, 1, 0) for ia in in_a]) == set_size)

    # A and B have the same sum: twice the sum of A is the sum of 1..n.
    solver.add(c5.Sum([c5.If(ia, 2 * j, 0) for j, ia in zip(numbers, in_a)]) == total)

    # A and B have the same sum of squares: twice the sum of squares in A is the sum of squares of 1..n.
    solver.add(c5.Sum([c5.If(ia, 2 * j * j, 0) for j, ia in zip(numbers, in_a)]) == total_sq)

    return solver, {"A": a, "B": b}


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
