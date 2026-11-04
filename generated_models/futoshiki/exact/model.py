# futoshiki: an Exact (Python) model from DCP Rosetta.
# Download the `futoshiki.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python futoshiki.py futoshiki.json

from exact import Exact


def create_model(instance):
    """Futoshiki: fill an n-by-n grid with the numbers 1 to n so that every row and column
    holds each number once, the given numbers are in place, and the inequality signs between
    neighbouring cells hold."""
    values = instance["values"]  # values[r][c] is the number given in row r, column c; 0 when the cell is empty
    lt = instance["lt"]  # each [i1, j1, i2, j2] is a sign: cell (i1, j1) holds less than cell (i2, j2)
    n_side = len(values)  # the grid is n_side cells wide and high

    solver = Exact()

    # Exact identifies its variables by name.
    # grid[r][c] is the number in row r, column c.
    grid = [[f"grid_{r}_{c}" for c in range(n_side)] for r in range(n_side)]
    # holds[r][c][d] is 1 when cell (r, c) holds the number d.
    holds = [[{} for _ in range(n_side)] for _ in range(n_side)]
    for r in range(n_side):
        for c in range(n_side):
            solver.addVariable(grid[r][c], 1, n_side)
            for d in range(1, n_side + 1):
                holds[r][c][d] = f"holds_{r}_{c}_{d}"
                solver.addVariable(holds[r][c][d], 0, 1)
            # Each cell holds exactly one number.
            solver.addConstraint([(1, holds[r][c][d]) for d in range(1, n_side + 1)], True, 1, True, 1)
            # The number in each cell is the d it holds.
            solver.addConstraint([(d, holds[r][c][d]) for d in range(1, n_side + 1)] + [(-1, grid[r][c])],
                                 True, 0, True, 0)
            # A given number stays in its cell.
            if values[r][c] > 0:
                solver.addConstraint([(1, holds[r][c][values[r][c]])], True, 1, True, 1)

    # Each row holds each number once.
    for d in range(1, n_side + 1):
        for r in range(n_side):
            solver.addConstraint([(1, holds[r][c][d]) for c in range(n_side)], True, 1, True, 1)

    # Each column holds each number once.
    for d in range(1, n_side + 1):
        for c in range(n_side):
            solver.addConstraint([(1, holds[r][c][d]) for r in range(n_side)], True, 1, True, 1)

    # Each sign: the cell at its start holds a smaller number than the cell at its end.
    for i1, j1, i2, j2 in lt:
        solver.addConstraint([(1, grid[i1 - 1][j1 - 1]), (-1, grid[i2 - 1][j2 - 1])], False, 0, True, -1)

    return solver, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
