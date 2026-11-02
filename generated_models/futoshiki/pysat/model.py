# futoshiki: a PySAT (Python) model from DCP Rosetta.
# Download the `futoshiki.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python futoshiki.py futoshiki.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Futoshiki: fill a square grid with the numbers 1 to n so that every row and every column
    holds each number once, the given numbers stand in their cells, and each inequality sign
    between neighbouring cells holds."""
    values = instance["values"]  # values[r][c]: the number given in row r, column c; 0 for an empty cell
    lt = instance["lt"]  # [r1, c1, r2, c2]: the cell in row r1, column c1 holds a smaller number than the cell in row r2, column c2 (counted from 1)
    size = len(values)  # the grid is size by size

    pool = IDPool()

    # grid[r][c] is the number in row r, column c, from 1 to size
    grid = [[Integer(f"grid_{r}_{c}", 1, size, vpool=pool) for c in range(size)] for r in range(size)]
    # All cells of the grid.
    cells = [cell for row in grid for cell in row]
    engine = IntegerEngine(vars=cells, vpool=pool)

    # The given numbers stand in their cells.
    for r in range(size):
        for c in range(size):
            if values[r][c] > 0:
                engine.add_linear(grid[r][c] == values[r][c])

    # Each row and each column holds every number once.
    for i in range(size):
        engine.add_alldifferent(grid[i])
        engine.add_alldifferent([grid[r][i] for r in range(size)])

    # Each inequality sign holds: the first cell holds a smaller number than the second.
    for r1, c1, r2, c2 in lt:
        engine.add_linear(grid[r1 - 1][c1 - 1] - grid[r2 - 1][c2 - 1] <= -1)

    return engine.clausify(), {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
