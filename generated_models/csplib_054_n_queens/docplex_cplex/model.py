# csplib_054_n_queens: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_054_n_queens.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_054_n_queens.py csplib_054_n_queens.json

from docplex.mp.model import Model


def create_model(instance):
    """N-queens: place n queens on an n-by-n board so that no two share a row, a column or a diagonal."""
    n = instance["n"]  # the board is n by n, with n queens
    rows = range(n)
    cols = range(n)

    model = Model("n_queens")

    # queen[i, j] is 1 when the queen of row i stands in column j.
    queen = model.binary_var_matrix(rows, cols, name="queen")

    # Every row has exactly one queen.
    model.add_constraints(model.sum(queen[i, j] for j in cols) == 1 for i in rows)

    # No two queens share a column.
    model.add_constraints(model.sum(queen[i, j] for i in rows) <= 1 for j in cols)

    # No two queens share a diagonal: squares with the same j - i lie on one
    # diagonal, and squares with the same j + i on one anti-diagonal.
    for d in range(-(n - 1), n):
        model.add_constraint(model.sum(queen[i, i + d] for i in rows if 0 <= i + d < n) <= 1,
                             ctname=f"diag_{d + n}")
    for s in range(2 * n - 1):
        model.add_constraint(model.sum(queen[i, s - i] for i in rows if 0 <= s - i < n) <= 1,
                             ctname=f"anti_{s}")

    # The column, 1-based, of the queen in each row.
    return model, {"queens": [model.sum((j + 1) * queen[i, j] for j in cols) for i in rows]}


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
