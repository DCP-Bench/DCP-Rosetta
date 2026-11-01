# csplib_076_costas_arrays: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_076_costas_arrays.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_076_costas_arrays.py csplib_076_costas_arrays.json

from pychoco.model import Model


def create_model(instance):
    """Place n marks on an n-by-n grid, one per row and one per column, so that the
    n(n-1)/2 vectors between the marks are all different (a Costas array)."""
    n = instance["n"]  # size of the grid and number of marks

    model = Model()

    # costas[j] is the row (1 to n) of the mark in column j
    costas = [model.intvar(1, n, name=f"costas_{j}") for j in range(n)]

    # One mark per row: the rows form a permutation.
    model.all_different(costas).post()

    # For each column distance d, the row differences between marks d columns apart
    # are all different. Distance n - 1 has a single pair, so it needs no constraint.
    for d in range(1, n - 1):
        differences = []  # all row differences at column distance d
        for j in range(d, n):
            # the row difference between the marks in columns j - d and j
            difference = model.intvar(-(n - 1), n - 1, name=f"difference_{d}_{j}")
            model.arithm(costas[j], "-", costas[j - d], "=", difference).post()
            differences.append(difference)
        model.all_different(differences).post()

    return model, {"costas": costas}, None


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
