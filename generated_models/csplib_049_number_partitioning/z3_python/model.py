# csplib_049_number_partitioning: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_049_number_partitioning.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_049_number_partitioning.py csplib_049_number_partitioning.json

import z3


def create_model(instance):
    """Partition the numbers 1 to n into two sets A and B of the same size, with the same
    sum and the same sum of squares."""
    n = instance["n"]        # the numbers 1 to n are split between A and B
    n_per_set = n // 2       # the size of each set

    # A[i] is the i-th number in set A
    A = [z3.Int(f"A_{i}") for i in range(n_per_set)]
    # B[i] is the i-th number in set B
    B = [z3.Int(f"B_{i}") for i in range(n_per_set)]

    solver = z3.Solver()

    # Each number is from 1 to n.
    solver.add([z3.And(x >= 1, x <= n) for x in A + B])

    # No number appears twice.
    solver.add(z3.Distinct(A + B))

    # A and B have the same sum.
    solver.add(z3.Sum(A) == z3.Sum(B))

    # A and B have the same sum of squares.
    solver.add(z3.Sum([x * x for x in A]) == z3.Sum([x * x for x in B]))

    return solver, {"A": A, "B": B}


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
