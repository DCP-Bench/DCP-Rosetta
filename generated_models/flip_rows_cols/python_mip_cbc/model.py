# flip_rows_cols: a Python-MIP (Python) model from DCP Rosetta.
# Download the `flip_rows_cols.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python flip_rows_cols.py flip_rows_cols.json

import itertools

import mip


def create_model(instance):
    """Flip the sign of whole rows and whole columns of a matrix of positive and negative
    numbers, so that every row and every column sums to zero or more. Choose the flips that
    make the sum of all the numbers as small as possible, and report the sign of each row
    and each column, as -1 or 1."""
    matrix = instance["input_matrix"]  # matrix[i][j]: the number in row i, column j
    n_rows = len(matrix)               # the number of rows
    n_cols = len(matrix[0])            # the number of columns

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # flipped[i] is 1 when row i is flipped, and 0 when not.
    flipped = [model.add_var(f"flipped_{i}", var_type=mip.BINARY) for i in range(n_rows)]

    # A pattern gives every column a sign, -1 or 1. There are 2^n_cols patterns.
    patterns = list(itertools.product((1, -1), repeat=n_cols))
    # chosen[k] is 1 when pattern k gives the column signs, and 0 when not.
    chosen = [model.add_var(f"chosen_{k}", var_type=mip.BINARY) for k in range(len(patterns))]
    # Exactly one pattern gives the column signs.
    model += mip.xsum(chosen) == 1

    # row_sums[k][i] is the sum of row i under pattern k, before row i is flipped.
    row_sums = [[sum(s[j] * matrix[i][j] for j in range(n_cols)) for i in range(n_rows)] for s in patterns]

    # Every row sums to zero or more after the flips. Under pattern k, a row with a positive sum
    # is not flipped, and a row with a negative sum is flipped. A row with sum zero can go either way.
    for k in range(len(patterns)):
        for i in range(n_rows):
            if row_sums[k][i] > 0:
                model.add_constr(flipped[i] <= 1 - chosen[k])
            elif row_sums[k][i] < 0:
                model.add_constr(flipped[i] >= chosen[k])

    # Every column sums to zero or more after the flips. Under pattern k, column j sums to its sign
    # times its total, minus twice the flipped entries of that column. A column sum is never below
    # minus column_bound, so the constraint holds for every flip when pattern k is not chosen.
    for k, s in enumerate(patterns):
        for j in range(n_cols):
            column_total = sum(matrix[i][j] for i in range(n_rows))
            # column_bound is the sum of the absolute values in column j.
            column_bound = sum(abs(matrix[i][j]) for i in range(n_rows))
            flips = mip.xsum(-2 * s[j] * matrix[i][j] * flipped[i] for i in range(n_rows))
            model += s[j] * column_total + flips + column_bound * (1 - chosen[k]) >= 0

    # The total of the flipped matrix. Each flipped row sums to the absolute value of its sum before
    # the flip, so the total under pattern k is the sum of those absolute values.
    model.objective = mip.xsum(sum(abs(R) for R in row_sums[k]) * chosen[k] for k in range(len(patterns)))

    # row_signs[i] is -1 when row i is flipped, and 1 when not.
    row_signs = [1 - 2 * flipped[i] for i in range(n_rows)]
    # col_signs[j] is the sign of column j under the chosen pattern.
    col_signs = [mip.xsum(patterns[k][j] * chosen[k] for k in range(len(patterns))) for j in range(n_cols)]

    return model, {"row_signs": row_signs, "col_signs": col_signs}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
