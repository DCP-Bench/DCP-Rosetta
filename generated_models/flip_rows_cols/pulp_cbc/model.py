# flip_rows_cols: a PuLP (Python) model from DCP Rosetta.
# Download the `flip_rows_cols.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python flip_rows_cols.py flip_rows_cols.json

import pulp


def create_model(instance):
    """Flip the sign of whole rows and columns of a matrix of positive and negative numbers,
    so that every row and every column sums to zero or more, and the total of the matrix is
    as small as possible."""
    matrix = instance["input_matrix"]  # matrix[i][j]: the number in row i and column j
    n_rows = len(matrix)               # the number of rows
    n_cols = len(matrix[0])            # the number of columns

    # abs_row[i] and abs_col[j]: the sums of the absolute values in row i and in column j.
    # The sum of a row or column after the flips is never larger in size than this.
    abs_row = [sum(abs(v) for v in matrix[i]) for i in range(n_rows)]
    abs_col = [sum(abs(matrix[i][j]) for i in range(n_rows)) for j in range(n_cols)]

    problem = pulp.LpProblem("flip_rows_cols", pulp.LpMinimize)

    # row_flip[i] is 1 when row i is flipped, and 0 when not
    row_flip = [pulp.LpVariable(f"row_flip_{i}", cat="Binary") for i in range(n_rows)]
    # col_flip[j] is 1 when column j is flipped, and 0 when not
    col_flip = [pulp.LpVariable(f"col_flip_{j}", cat="Binary") for j in range(n_cols)]

    # row_signs[i] and col_signs[j]: the sign of row i and of column j, +1 when not flipped and -1 when flipped
    row_signs = [1 - 2 * f for f in row_flip]
    col_signs = [1 - 2 * f for f in col_flip]

    # row_sum[i] is the sum of row i after the flips, and it is zero or more.
    # When row i is not flipped, its sum is the sum of row i with the column flips applied;
    # when it is flipped, its sum is the negative of that. Each of the four inequalities
    # describes one of the two cases; in the other case it is loose, because the sum never
    # exceeds the row's absolute total in size.
    row_sum = []
    for i in range(n_rows):
        unflipped_row_sum = pulp.lpSum(matrix[i][j] * col_signs[j] for j in range(n_cols))
        total_i = pulp.LpVariable(f"row_sum_{i}", 0, abs_row[i])
        problem += total_i >= unflipped_row_sum - 2 * abs_row[i] * row_flip[i]
        problem += total_i <= unflipped_row_sum + 2 * abs_row[i] * row_flip[i]
        problem += total_i >= -unflipped_row_sum - 2 * abs_row[i] * (1 - row_flip[i])
        problem += total_i <= -unflipped_row_sum + 2 * abs_row[i] * (1 - row_flip[i])
        row_sum.append(total_i)

    # col_sum[j] is the sum of column j after the flips, and it is zero or more.
    # The same two cases apply as for the rows, with the row flips in place of the column flips.
    col_sum = []
    for j in range(n_cols):
        unflipped_col_sum = pulp.lpSum(matrix[i][j] * row_signs[i] for i in range(n_rows))
        total_j = pulp.LpVariable(f"col_sum_{j}", 0, abs_col[j])
        problem += total_j >= unflipped_col_sum - 2 * abs_col[j] * col_flip[j]
        problem += total_j <= unflipped_col_sum + 2 * abs_col[j] * col_flip[j]
        problem += total_j >= -unflipped_col_sum - 2 * abs_col[j] * (1 - col_flip[j])
        problem += total_j <= -unflipped_col_sum + 2 * abs_col[j] * (1 - col_flip[j])
        col_sum.append(total_j)

    # total_sum is the total of the matrix after the flips. It is the sum of the row sums and
    # also the sum of the column sums.
    total_sum = pulp.LpVariable("total_sum", 0, sum(abs_row))
    problem += total_sum == pulp.lpSum(row_sum)
    problem += total_sum == pulp.lpSum(col_sum)

    # Make the total as small as possible.
    problem += total_sum

    return problem, {"row_signs": row_signs, "col_signs": col_signs}


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
