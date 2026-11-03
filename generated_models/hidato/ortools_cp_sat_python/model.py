# hidato: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `hidato.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
# Then run it on the first instance (after `pip install ortools`):
#   python hidato.py hidato.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Hidato puzzles start semi-filled with numbered tiles. Fill the grid with the
    numbers 1 to r*c, each used once, keeping the given numbers, so that every
    number k and the next number k+1 sit in cells that touch horizontally,
    vertically or diagonally."""
    puzzle = instance["puzzle"]  # the grid; a 0 marks an empty cell
    n_rows, n_cols = len(puzzle), len(puzzle[0])
    n_cells = n_rows * n_cols

    model = cp_model.CpModel()

    # at[i][j][k] is true when cell (i, j) holds the number k + 1.
    at = [[[model.new_bool_var(f"at_{i}_{j}_{k}") for k in range(n_cells)]
           for j in range(n_cols)]
          for i in range(n_rows)]
    # x[i][j] is the number in cell (i, j)
    x = [[model.new_int_var(1, n_cells, f"x_{i}_{j}") for j in range(n_cols)]
         for i in range(n_rows)]

    # Each cell holds exactly one number, and x gives that number.
    for i in range(n_rows):
        for j in range(n_cols):
            model.add_exactly_one(at[i][j])
            model.add(x[i][j] == sum((k + 1) * at[i][j][k] for k in range(n_cells)))

    # Each number is used in exactly one cell.
    for k in range(n_cells):
        model.add_exactly_one(at[i][j][k] for i in range(n_rows) for j in range(n_cols))

    # The given numbers stay where they are.
    for i in range(n_rows):
        for j in range(n_cols):
            if puzzle[i][j] > 0:
                model.add(at[i][j][puzzle[i][j] - 1] == 1)

    # If number k is in a cell, number k+1 is in one of its neighbours.
    for i in range(n_rows):
        for j in range(n_cols):
            # The neighbours of cell (i, j), not counting the cell itself.
            near = [
                (a, b)
                for a in range(max(0, i - 1), min(n_rows, i + 2))
                for b in range(max(0, j - 1), min(n_cols, j + 2))
                if (a, b) != (i, j)
            ]
            for k in range(n_cells - 1):
                model.add_bool_or([at[a][b][k + 1] for a, b in near]).only_enforce_if(at[i][j][k])

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
