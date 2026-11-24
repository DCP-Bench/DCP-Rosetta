# coins_grid: a CPLEX (Python) model from DCP Rosetta.
# Download the `coins_grid.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python coins_grid.py coins_grid.json

from docplex.mp.model import Model


def create_model(instance):
    """Coins grid: place coins on an n by n grid, c in every row and every column, so that the sum
    of the squared horizontal distances of the coins from the main diagonal is as small as possible."""
    n = instance["n"]  # size of the grid (n by n)
    c = instance["c"]  # coins in each row and each column

    model = Model("coins_grid")

    # x[i][j] is 1 when a coin is placed in the cell of row i and column j (at most one coin
    # per cell).
    x = [[model.binary_var(name=f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    # Every row holds exactly c coins.
    model.add_constraints(model.sum(x[i][j] for j in range(n)) == c for i in range(n))

    # Every column holds exactly c coins.
    model.add_constraints(model.sum(x[i][j] for i in range(n)) == c for j in range(n))

    # z is the sum, over the cells with a coin, of the squared horizontal distance from the
    # main diagonal; it is the objective.
    z = model.sum(x[i][j] * (i - j) ** 2 for i in range(n) for j in range(n))
    model.minimize(z)

    return model, {"x": x, "z": z}


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
