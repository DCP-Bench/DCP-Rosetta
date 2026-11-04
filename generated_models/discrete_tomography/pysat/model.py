# discrete_tomography: a PySAT (Python) model from DCP Rosetta.
# Download the `discrete_tomography.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python discrete_tomography.py discrete_tomography.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """A matrix of zeroes and ones is x-rayed vertically and horizontally, giving the
    number of ones in each row and column. Reconstruct the matrix."""
    row_sums = instance["row_sums"]  # row_sums[i]: the number of ones in row i
    col_sums = instance["col_sums"]  # col_sums[j]: the number of ones in column j
    n_rows, n_cols = len(row_sums), len(col_sums)

    pool = IDPool()  # names the variables of the model

    # matrix[i][j] is 1 when the cell in row i, column j holds a one, and 0 otherwise
    matrix = [[Integer(f"m{i}_{j}", 0, 1, vpool=pool) for j in range(n_cols)]
              for i in range(n_rows)]
    cells = [cell for row in matrix for cell in row]  # every cell of the matrix
    engine = IntegerEngine(vars=cells, vpool=pool)  # the row and column counts

    # Each row contains the given number of ones.
    for i in range(n_rows):
        engine.add_linear(sum(matrix[i][j] for j in range(n_cols)) == row_sums[i])
    # Each column contains the given number of ones.
    for j in range(n_cols):
        engine.add_linear(sum(matrix[i][j] for i in range(n_rows)) == col_sums[j])

    return engine.clausify(), {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
