# flip_rows_cols: a Z3 (Python) model from DCP Rosetta.
# Download the `flip_rows_cols.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python flip_rows_cols.py flip_rows_cols.json

import z3


def create_model(instance):
    """Flip the signs of whole rows and whole columns of a matrix of positive and negative
    numbers, as many as you like, so that every row and every column of the result sums to
    zero or more. Among such flips, make the total of all entries as small as possible.
    The answer is the sign of each row and of each column, -1 if flipped and 1 if not."""
    matrix = instance["input_matrix"]  # matrix[i][j]: the number in row i, column j
    n_rows = len(matrix)               # number of rows
    n_cols = len(matrix[0])            # number of columns

    # row_flipped[i] is true when row i is flipped; col_flipped[j] is true when column j is flipped
    row_flipped = [z3.Bool(f"row_flipped_{i}") for i in range(n_rows)]
    col_flipped = [z3.Bool(f"col_flipped_{j}") for j in range(n_cols)]

    # row_signs[i] and col_signs[j] are the signs of row i and of column j
    row_signs = [z3.Int(f"row_signs_{i}") for i in range(n_rows)]
    col_signs = [z3.Int(f"col_signs_{j}") for j in range(n_cols)]

    # row_sums[i] and col_sums[j] are the sums of row i and of column j after flipping
    row_sums = [z3.Int(f"row_sums_{i}") for i in range(n_rows)]
    col_sums = [z3.Int(f"col_sums_{j}") for j in range(n_cols)]

    # total is the sum of all entries after flipping
    total = z3.Int("total")

    solver = z3.Optimize()

    # The sign of a flipped row or column is -1, and the sign of an unflipped one is 1.
    solver.add([row_signs[i] == z3.If(row_flipped[i], -1, 1) for i in range(n_rows)])
    solver.add([col_signs[j] == z3.If(col_flipped[j], -1, 1) for j in range(n_cols)])

    # signed[i][j] is the entry in row i and column j after flipping. It keeps its sign when its
    # row and column are both flipped or both unflipped, and changes sign when only one is flipped.
    signed = [[z3.If(row_flipped[i] == col_flipped[j], matrix[i][j], -matrix[i][j])
               for j in range(n_cols)] for i in range(n_rows)]

    # Every row and every column of the flipped matrix sums to zero or more.
    for i in range(n_rows):
        solver.add(row_sums[i] == z3.Sum(signed[i]))
        solver.add(row_sums[i] >= 0)
    for j in range(n_cols):
        solver.add(col_sums[j] == z3.Sum([signed[i][j] for i in range(n_rows)]))
        solver.add(col_sums[j] >= 0)

    # The total is the sum of the row sums.
    solver.add(total == z3.Sum(row_sums))

    solver.minimize(total)

    return solver, {"row_signs": row_signs, "col_signs": col_signs}


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
