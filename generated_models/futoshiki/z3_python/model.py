# futoshiki: a Z3 (Python) model from DCP Rosetta.
# Download the `futoshiki.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python futoshiki.py futoshiki.json

import z3


def create_model(instance):
    """Futoshiki: fill an n-by-n grid with the numbers 1 to n so that every row and column holds
    each number once, the given numbers are in place, and each inequality sign holds."""
    values = instance["values"]  # values[r][c]: the number given in row r, column c; 0 when the cell is empty
    # each [r1, c1, r2, c2]: the cell in row r1, column c1 is smaller than the cell in row r2,
    # column c2 (rows and columns counted from 1)
    lt = instance["lt"]
    size = len(values)  # the grid is size by size

    # grid[r][c] is the number in row r, column c
    grid = [[z3.Int(f"grid_{r}_{c}") for c in range(size)] for r in range(size)]

    solver = z3.Solver()

    # Each cell holds a number from 1 to size.
    solver.add([z3.And(1 <= grid[r][c], grid[r][c] <= size) for r in range(size) for c in range(size)])

    # The given numbers are in place.
    solver.add([grid[r][c] == values[r][c] for r in range(size) for c in range(size) if values[r][c] > 0])

    # Every row contains each number once.
    solver.add([z3.Distinct(row) for row in grid])

    # Every column contains each number once.
    solver.add([z3.Distinct([grid[r][c] for r in range(size)]) for c in range(size)])

    # Every inequality sign holds.
    solver.add([grid[r1 - 1][c1 - 1] < grid[r2 - 1][c2 - 1] for r1, c1, r2, c2 in lt])

    return solver, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
