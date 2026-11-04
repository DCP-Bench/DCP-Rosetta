# discrete_tomography: a PuLP (Python) model from DCP Rosetta.
# Download the `discrete_tomography.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python discrete_tomography.py discrete_tomography.json

import pulp


def create_model(instance):
    """A matrix of zeroes and ones is "x-rayed" vertically and horizontally,
    giving the number of ones in each row and column. Reconstruct the matrix."""
    row_sums = instance["row_sums"]  # row_sums[i]: the number of ones in row i
    col_sums = instance["col_sums"]  # col_sums[j]: the number of ones in column j
    n_rows = len(row_sums)           # the number of rows
    n_cols = len(col_sums)           # the number of columns

    problem = pulp.LpProblem("discrete_tomography", pulp.LpMinimize)

    # matrix[i][j] is 1 when the cell in row i, column j holds a one, and 0 otherwise
    matrix = [
        [pulp.LpVariable(f"cell_{i}_{j}", cat="Binary") for j in range(n_cols)]
        for i in range(n_rows)
    ]

    # Each row contains the given number of ones.
    for row, total in zip(matrix, row_sums):
        problem += pulp.lpSum(row) == total
    # Each column contains the given number of ones.
    for j, total in enumerate(col_sums):
        problem += pulp.lpSum(matrix[i][j] for i in range(n_rows)) == total

    return problem, {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
