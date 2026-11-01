# futoshiki: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `futoshiki.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
# Then run it on the first instance (after `pip install ortools`):
#   python futoshiki.py futoshiki.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Futoshiki: fill an n-by-n grid with the numbers 1 to n so that every row and
    column holds each number once, the given numbers are in place, and the
    inequality signs between neighbouring cells hold."""
    values = instance["values"]  # the numbers given at the start, by row and column
    lt = instance["lt"]          # the inequality signs; each names the smaller cell, then the larger, by row and column
    size = len(values)           # the number of rows and columns

    model = cp_model.CpModel()

    # grid[i][j] is the number in row i, column j. A given number fixes its cell;
    # an empty cell can hold any number from 1 to size.
    grid = [[model.new_int_var(values[i][j] or 1, values[i][j] or size, f"grid_{i}_{j}")
             for j in range(size)] for i in range(size)]

    # Every row contains each number once.
    for row in grid:
        model.add_all_different(row)

    # Every column contains each number once.
    for j in range(size):
        model.add_all_different([grid[i][j] for i in range(size)])

    # Every inequality sign holds: the first cell is smaller than the second.
    for i1, j1, i2, j2 in lt:
        model.add(grid[i1 - 1][j1 - 1] < grid[i2 - 1][j2 - 1])

    return model, {"grid": grid}


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
