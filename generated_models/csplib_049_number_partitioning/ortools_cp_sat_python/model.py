# csplib_049_number_partitioning: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_049_number_partitioning.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_049_number_partitioning.py csplib_049_number_partitioning.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Partition the numbers 1..n into two sets A and B of the same size, with
    the same sum and the same sum of squares."""
    n = instance["n"]          # the numbers 1..n are partitioned
    n_per_set = n // 2         # the size of each set

    model = cp_model.CpModel()

    # a[i] is the i-th number of set A
    a = [model.new_int_var(1, n, f"A_{i}") for i in range(n_per_set)]
    # b[i] is the i-th number of set B
    b = [model.new_int_var(1, n, f"B_{i}") for i in range(n_per_set)]

    # No number is used twice.
    model.add_all_different(a + b)
    # A and B have the same sum.
    model.add(sum(a) == sum(b))

    # sq_a[i] and sq_b[i] are the squares of a[i] and b[i]
    sq_a = [model.new_int_var(1, n * n, f"square_A_{i}") for i in range(n_per_set)]
    sq_b = [model.new_int_var(1, n * n, f"square_B_{i}") for i in range(n_per_set)]
    # Each square is the square of its number.
    for x, sq in zip(a + b, sq_a + sq_b):
        model.add_multiplication_equality(sq, [x, x])
    # A and B have the same sum of squares.
    model.add(sum(sq_a) == sum(sq_b))

    return model, {"A": a, "B": b}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
