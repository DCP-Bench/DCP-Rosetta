# futoshiki: a Choco-solver (Python) model from DCP Rosetta.
# Download the `futoshiki.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python futoshiki.py futoshiki.json

from pychoco.model import Model


def create_model(instance):
    """Futoshiki: fill an n-by-n grid with the numbers 1 to n so that every row and
    column holds each number once, the given numbers are in place, and the
    inequality signs between neighbouring cells hold."""
    values = instance["values"]  # values[i][j]: the number given in row i, column j; 0 means empty
    lt = instance["lt"]  # each [i1, j1, i2, j2]: the cell (i1, j1) is smaller than the cell (i2, j2)
    size = len(values)  # the number of rows and columns

    model = Model()

    # grid[i][j] is the number in row i, column j; a given number is the only value its cell can take
    grid = [[model.intvar(values[i][j] or 1, values[i][j] or size, name=f"grid_{i}_{j}")
             for j in range(size)] for i in range(size)]

    # Every row contains each number once.
    for row in grid:
        model.all_different(row).post()

    # Every column contains each number once.
    for j in range(size):
        model.all_different([grid[i][j] for i in range(size)]).post()

    # Every inequality sign holds.
    for i1, j1, i2, j2 in lt:
        model.arithm(grid[i1 - 1][j1 - 1], "<", grid[i2 - 1][j2 - 1]).post()

    return model, {"grid": grid}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
