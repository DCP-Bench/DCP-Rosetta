# flip_rows_cols: a PyCSP3 model from DCP Rosetta.
# Download the `flip_rows_cols.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python flip_rows_cols.py flip_rows_cols.json

from pycsp3 import *


def create_model(instance):
    """Flip the sign of entire rows and columns, as many as you like, so that every row
    and every column sums to a positive number or zero. Among these choices, find the
    signs of the rows and of the columns that make the overall sum of the array as small
    as possible."""
    matrix = instance["input_matrix"]  # matrix[i][j] is the number in row i and column j
    n_rows = len(matrix)
    n_cols = len(matrix[0])
    # The two signs of a row or column: -1 when it is flipped, 1 when it is not.
    signs = [-1, 1]

    # row_sign[i] is the sign of row i.
    row_sign = VarArray(size=n_rows, dom=signs)
    # col_sign[j] is the sign of column j.
    col_sign = VarArray(size=n_cols, dom=signs)

    satisfy(
        # Every row sums to a positive number or zero, after each entry is multiplied by the signs of its row and its column.
        [Sum(matrix[i][j] * row_sign[i] * col_sign[j] for j in range(n_cols)) >= 0
         for i in range(n_rows)],
        # Every column sums to a positive number or zero, after each entry is multiplied by the signs of its row and its column.
        [Sum(matrix[i][j] * row_sign[i] * col_sign[j] for i in range(n_rows)) >= 0
         for j in range(n_cols)],
    )

    # The overall sum of the array, after the flips, is as small as possible.
    minimize(Sum(matrix[i][j] * row_sign[i] * col_sign[j]
                 for i in range(n_rows) for j in range(n_cols)))

    return {"row_signs": row_sign, "col_signs": col_sign}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
