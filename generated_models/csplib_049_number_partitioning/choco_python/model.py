# csplib_049_number_partitioning: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_049_number_partitioning.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_049_number_partitioning.py csplib_049_number_partitioning.json

from pychoco.model import Model


def create_model(instance):
    """Split the numbers 1 to n into two sets A and B of the same size, with the same sum
    and the same sum of squares."""
    n = instance["n"]  # the numbers 1 to n to be split
    half = n // 2      # how many numbers each set holds

    model = Model()

    # A[i] and B[i] are the i-th numbers of sets A and B
    a = [model.intvar(1, n, name=f"A_{i}") for i in range(half)]
    b = [model.intvar(1, n, name=f"B_{i}") for i in range(half)]

    # Every number from 1 to n is used once, in A or in B.
    model.all_different(a + b).post()

    # Sets A and B have the same sum.
    model.scalar(a + b, [1] * half + [-1] * half, "=", 0).post()

    # a_sq[i] and b_sq[i] are the squares of A[i] and B[i].
    a_sq = [model.intvar(1, n * n, name=f"A_sq_{i}") for i in range(half)]
    b_sq = [model.intvar(1, n * n, name=f"B_sq_{i}") for i in range(half)]
    for x, sq in zip(a + b, a_sq + b_sq):
        model.square(sq, x).post()

    # Sets A and B have the same sum of squares.
    model.scalar(a_sq + b_sq, [1] * half + [-1] * half, "=", 0).post()

    return model, {"A": a, "B": b}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
