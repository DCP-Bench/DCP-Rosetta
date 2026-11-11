# flip_rows_cols: a CPLEX (Python) model from DCP Rosetta.
# Download the `flip_rows_cols.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python flip_rows_cols.py flip_rows_cols.json

from docplex.mp.model import Model


def create_model(instance):
    """Flip rows and columns: choose a sign (+1 or -1) for every row and every column of a matrix,
    each entry being multiplied by its row's and its column's sign, so that every row sum and
    every column sum is non-negative and the total sum is as small as possible."""
    matrix = instance["input_matrix"]  # matrix[i][j]: the number in row i, column j
    rows = range(len(matrix))
    cols = range(len(matrix[0]))

    model = Model("flip_rows_cols")

    # row_up[i] is 1 when row i keeps its sign (+1) and 0 when it is flipped (-1); col_up[j]
    # likewise for column j. A sign is never 0.
    row_up = [model.binary_var(name=f"row_up_{i}") for i in rows]
    col_up = [model.binary_var(name=f"col_up_{j}") for j in cols]
    # row_signs[i] and col_signs[j] are the signs, +1 or -1, of row i and column j.
    row_signs = [2 * row_up[i] - 1 for i in rows]
    col_signs = [2 * col_up[j] - 1 for j in cols]

    # Each entry is the input entry times its row sign times its column sign. The product of
    # the two signs is 4 * both - 2 * row_up - 2 * col_up + 1, where both[i, j] is the product
    # row_up[i] * col_up[j], pinned down by three linear constraints (a product of two
    # variables would be a non-convex quadratic constraint, which CPLEX refuses).
    both = {}
    for i in rows:
        for j in cols:
            both[i, j] = model.continuous_var(0, 1, name=f"both_{i}_{j}")
            model.add_constraint(both[i, j] <= row_up[i])
            model.add_constraint(both[i, j] <= col_up[j])
            model.add_constraint(both[i, j] >= row_up[i] + col_up[j] - 1)
    x = {(i, j): matrix[i][j] * (4 * both[i, j] - 2 * row_up[i] - 2 * col_up[j] + 1)
         for i in rows for j in cols}

    # Every row and every column sums to a positive number or zero.
    model.add_constraints(model.sum(x[i, j] for j in cols) >= 0 for i in rows)
    model.add_constraints(model.sum(x[i, j] for i in rows) >= 0 for j in cols)

    # The overall sum is as small as possible.
    model.minimize(model.sum(x.values()))

    return model, {"row_signs": row_signs, "col_signs": col_signs}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
