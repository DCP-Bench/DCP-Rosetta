# discrete_tomography: a hermax (Python) model from DCP Rosetta.
# Download the `discrete_tomography.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
# Then run it on the first instance (after `pip install hermax`):
#   python discrete_tomography.py discrete_tomography.json

from hermax.model import Model


def create_model(instance):
    """Discrete tomography: find a matrix of zeros and ones whose row sums and column
    sums are the given numbers, i.e. each row contains exactly row_sums[i] ones and
    each column exactly col_sums[j] ones. Satisfaction problem, no objective."""
    # row_sums[i]: the number of ones in row i of the matrix
    row_sums = instance["row_sums"]
    # col_sums[j]: the number of ones in column j of the matrix
    col_sums = instance["col_sums"]

    # The matrix size follows the data of this instance.
    n_rows = len(row_sums)
    n_cols = len(col_sums)

    m = Model()

    # matrix[i][j] is 1 when cell (i, j) holds a one, 0 otherwise
    matrix = m.int_matrix("matrix", n_rows, n_cols, 0, 1)

    # Each row contains exactly row_sums[i] ones.
    for i in range(n_rows):
        m &= (sum(matrix.row(i)) == row_sums[i])

    # Each column contains exactly col_sums[j] ones.
    for j in range(n_cols):
        m &= (sum(matrix.col(j)) == col_sums[j])

    return m, {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
