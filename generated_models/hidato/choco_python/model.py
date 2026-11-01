# hidato: a Choco-solver (Python) model from DCP Rosetta.
# Download the `hidato.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python hidato.py hidato.json

from pychoco.model import Model


def create_model(instance):
    """Hidato: fill the empty cells of a grid with the numbers 1 to r*c, each used once,
    so that every number and the next one sit in cells that touch horizontally,
    vertically or diagonally. The numbers already in the grid stay where they are."""
    puzzle = instance["puzzle"]  # puzzle[i][j] is the given number in row i, column j, or 0 if empty
    n_rows, n_cols = len(puzzle), len(puzzle[0])
    n_cells = n_rows * n_cols

    model = Model()

    # number_in[c - 1] is the number written in cell c. Cells are numbered 1 to n_cells, row by row.
    number_in = [model.intvar(1, n_cells, name=f"number_in_{c}") for c in range(1, n_cells + 1)]
    # cell_of[v - 1] is the cell that holds the number v
    cell_of = [model.intvar(1, n_cells, name=f"cell_of_{v}") for v in range(1, n_cells + 1)]

    # Every number from 1 to n_cells is used once, and cell_of tells where each one is.
    model.all_different(number_in).post()
    model.inverse_channeling(number_in, cell_of, 1, 1).post()

    # Each given number stays in its cell.
    for i in range(n_rows):
        for j in range(n_cols):
            if puzzle[i][j] > 0:
                model.arithm(number_in[i * n_cols + j], "=", puzzle[i][j]).post()

    # Pairs of cells that touch, diagonals included.
    touching_cells = [[i * n_cols + j + 1, (i + di) * n_cols + (j + dj) + 1]
                      for i in range(n_rows) for j in range(n_cols)
                      for di in (-1, 0, 1) for dj in (-1, 0, 1)
                      if (di, dj) != (0, 0) and 0 <= i + di < n_rows and 0 <= j + dj < n_cols]

    # The cell of each number touches the cell of the next number.
    for v in range(1, n_cells):
        model.table([cell_of[v - 1], cell_of[v]], touching_cells).post()

    # The grid as written: x[i][j] is the number in row i, column j.
    x = [[number_in[i * n_cols + j] for j in range(n_cols)] for i in range(n_rows)]
    return model, {"x": x}, None


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
