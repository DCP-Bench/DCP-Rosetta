# discrete_tomography: a CPLEX (Python) model from DCP Rosetta.
# Download the `discrete_tomography.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python discrete_tomography.py discrete_tomography.json

from docplex.mp.model import Model


def create_model(instance):
    """Discrete tomography: rebuild a 0/1 matrix from the number of ones in each row and each column."""
    row_sums = instance["row_sums"]  # row_sums[i]: the number of ones in row i
    col_sums = instance["col_sums"]  # col_sums[j]: the number of ones in column j
    rows = range(len(row_sums))
    cols = range(len(col_sums))

    model = Model("discrete_tomography")

    # matrix[i, j] is the 0/1 entry in row i, column j.
    matrix = model.binary_var_matrix(rows, cols, name="matrix")

    # Each row holds as many ones as its x-ray says.
    for i in rows:
        model.add_constraint(model.sum(matrix[i, j] for j in cols) == row_sums[i], ctname=f"row_{i}")

    # Each column holds as many ones as its x-ray says.
    for j in cols:
        model.add_constraint(model.sum(matrix[i, j] for i in rows) == col_sums[j], ctname=f"col_{j}")

    return model, {"matrix": [[matrix[i, j] for j in cols] for i in rows]}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
