# hidato: a PySAT (Python) model from DCP Rosetta.
# Download the `hidato.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python hidato.py hidato.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Hidato: fill a grid with the numbers 1 to rows * columns, each once, so that every
    number sits in a cell that touches the cell of the number before it, horizontally,
    vertically or diagonally. The numbers already on the grid stay where they are."""
    puzzle = instance["puzzle"]  # puzzle[r][c] is the number given in row r, column c; 0 marks an empty cell
    rows, cols = len(puzzle), len(puzzle[0])  # the size of the grid
    last = rows * cols                         # the largest number, which is also the number of cells

    def touching(r, c):
        """The cells that touch (r, c) horizontally, vertically or diagonally."""
        return [(r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                if (dr, dc) != (0, 0) and 0 <= r + dr < rows and 0 <= c + dc < cols]

    pool = IDPool()

    # x[r][c] is the number in row r, column c
    x = [[Integer(f"x_{r}_{c}", 1, last, vpool=pool) for c in range(cols)] for r in range(rows)]
    cells = [cell for row in x for cell in row]
    engine = IntegerEngine(vars=cells, vpool=pool)

    # Every number is used once.
    engine.add_alldifferent(cells)
    formula = engine.clausify()

    # The numbers already on the grid stay in their cells.
    for r in range(rows):
        for c in range(cols):
            if puzzle[r][c] > 0:
                formula.append([x[r][c].equals(puzzle[r][c])])

    # If the number k is in a cell, the number k+1 is in a cell that touches it.
    for r in range(rows):
        for c in range(cols):
            for k in range(1, last):
                formula.append([-x[r][c].equals(k)] + [x[nr][nc].equals(k + 1) for nr, nc in touching(r, c)])

    # Read backwards: if the number k is in a cell, the number k-1 is in a cell that touches it.
    for r in range(rows):
        for c in range(cols):
            for k in range(2, last + 1):
                formula.append([-x[r][c].equals(k)] + [x[nr][nc].equals(k - 1) for nr, nc in touching(r, c)])

    return formula, {"x": x}


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
