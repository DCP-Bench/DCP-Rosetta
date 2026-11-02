# kakuro: a PySAT (Python) model from DCP Rosetta.
# Download the `kakuro.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python kakuro.py kakuro.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Insert a digit from 1 to 9 into each white cell of the grid so that the digits of
    each entry add up to its clue and no digit is repeated within an entry."""
    n = instance["n"]              # the grid is n by n
    blanks = instance["blanks"]    # [row, col] (1-based) of each black cell
    entries = instance["problem"]  # each entry is [clue, [row, col], ...]: its clue, then its cells (1-based)

    pool = IDPool()

    # x[r][c] is the digit in the cell at row r, column c (0-based)
    x = [[Integer(f"x_{r}_{c}", 0, 9, vpool=pool) for c in range(n)] for r in range(n)]
    engine = IntegerEngine(vars=[cell for row in x for cell in row], vpool=pool)

    # Black cells hold 0.
    for r, c in blanks:
        engine.add_linear(x[r - 1][c - 1] == 0)

    for clue, *cells in entries:
        # The digits in the cells of the entry.
        run = [x[r - 1][c - 1] for r, c in cells]
        # The cells of an entry are white, so each holds a digit from 1 to 9.
        for cell in run:
            engine.add_linear(cell >= 1)
        # The digits of the entry add up to its clue.
        engine.add_linear(sum(run) == clue)
        # No digit is repeated within the entry.
        engine.add_alldifferent(run)

    return engine.clausify(), {"x": x}


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
