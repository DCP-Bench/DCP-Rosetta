# csplib_032_max_density_still_life: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_032_max_density_still_life.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_032_max_density_still_life.py csplib_032_max_density_still_life.json

from docplex.mp.model import Model


def create_model(instance):
    """Maximum density still life: on an n-by-m patch of Conway's Game of Life board (every cell
    outside it dead), find a pattern that does not change from one generation to the next with as
    many live cells as possible."""
    n = instance["n"]  # rows of the active grid
    m = instance["m"]  # columns of the active grid

    model = Model("still_life")

    # grid[i][j] is 1 when cell (i, j) of the active grid is alive, and 0 when it is dead
    grid = [[model.binary_var(name=f"grid_{i}_{j}") for j in range(m)] for i in range(n)]

    # The pattern is stable: every cell of the grid keeps its state in the next generation.
    for i in range(n):
        for j in range(m):
            around = [grid[i + a][j + b] for a in (-1, 0, 1) for b in (-1, 0, 1)
                      if (a, b) != (0, 0) and 0 <= i + a < n and 0 <= j + b < m]
            k = model.sum(around)  # live neighbours of cell (i, j)
            deg = len(around)
            alive = grid[i][j]

            # A live cell has exactly 2 or 3 live neighbours (the bounds switch off when dead).
            model.add_constraint(k >= 2 * alive)
            if deg > 3:  # with at most 3 neighbours the upper bound holds anyway
                model.add_constraint(k <= 3 + (deg - 3) * (1 - alive))

            # A dead cell does not have exactly 3 live neighbours: it has at most 2 (many = 0)
            # or at least 4 (many = 1). Both bounds are relaxed for a live cell.
            many = model.binary_var(name=f"many_{i}_{j}")
            model.add_constraint(k <= 2 + max(0, deg - 2) * many + alive)
            model.add_constraint(k >= 4 * many - 4 * alive)

    # Cells just outside the grid are dead and must not be born: an outside cell next to three
    # cells of the grid's border must not see all three alive. Outside cells that touch fewer
    # border cells can never see three.
    windows = []
    for j in range(1, m - 1):
        windows.append([grid[0][j - 1], grid[0][j], grid[0][j + 1]])
        windows.append([grid[n - 1][j - 1], grid[n - 1][j], grid[n - 1][j + 1]])
    for i in range(1, n - 1):
        windows.append([grid[i - 1][0], grid[i][0], grid[i + 1][0]])
        windows.append([grid[i - 1][m - 1], grid[i][m - 1], grid[i + 1][m - 1]])
    for w in windows:
        model.add_constraint(model.sum(w) <= 2)

    # Maximize the number of live cells.
    model.maximize(model.sum(grid[i][j] for i in range(n) for j in range(m)))

    return model, {"grid": grid}


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
