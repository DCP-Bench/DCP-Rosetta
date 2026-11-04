# csplib_049_number_partitioning: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_049_number_partitioning.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_049_number_partitioning.py csplib_049_number_partitioning.json

from exact import Exact


def create_model(instance):
    """Partition the numbers 1 to n into two sets A and B of the same size, with the same sum
    and the same sum of squares."""
    n = instance["n"]  # the numbers 1 to n are split between A and B
    half = n // 2      # the size of each set

    solver = Exact()

    # Exact identifies its variables by name.
    # A[i] is the i-th number of set A, and B[i] the i-th number of set B; each is from 1 to n.
    A = [f"A_{i}" for i in range(half)]
    B = [f"B_{i}" for i in range(half)]
    for name in A + B:
        solver.addVariable(name, 1, n)

    # is_A[i][v - 1] is 1 when A[i] is the number v, and 0 when not. The same holds for B.
    is_A = [[f"A_{i}_is_{v}" for v in range(1, n + 1)] for i in range(half)]
    is_B = [[f"B_{i}_is_{v}" for v in range(1, n + 1)] for i in range(half)]
    for values, is_v in ((A, is_A), (B, is_B)):
        for i in range(half):
            for name in is_v[i]:
                solver.addVariable(name, 0, 1)
            # Each number of the set is exactly one value.
            solver.addConstraint([(1, name) for name in is_v[i]], True, 1, True, 1)
            # The number of the set is the value its flags mark.
            solver.addConstraint([(v, is_v[i][v - 1]) for v in range(1, n + 1)] + [(-1, values[i])], True, 0, True, 0)

    # Every number from 1 to n is in exactly one of the two sets.
    for v in range(1, n + 1):
        solver.addConstraint([(1, is_A[i][v - 1]) for i in range(half)]
                             + [(1, is_B[i][v - 1]) for i in range(half)], True, 1, True, 1)

    # The two sets have the same sum.
    solver.addConstraint([(1, name) for name in A] + [(-1, name) for name in B], True, 0, True, 0)

    # The two sets have the same sum of squares.
    solver.addConstraint([(v * v, is_A[i][v - 1]) for i in range(half) for v in range(1, n + 1)]
                         + [(-v * v, is_B[i][v - 1]) for i in range(half) for v in range(1, n + 1)],
                         True, 0, True, 0)

    return solver, {"A": A, "B": B}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
