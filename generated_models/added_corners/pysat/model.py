# added_corners: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python added_corners.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Enter the digits 1 through 8 in the circles and squares of a ring such that
    the number in each square is equal to the sum of the adjoining circles."""
    n_cells = 8  # the digits 1 through 8, one per circle and square

    pool = IDPool()

    # The digits in the ring, in reading order a b c / d e / f g h: cells[i] is the digit in cell i.
    cells = [Integer(f"p{i}", 1, n_cells, vpool=pool) for i in range(n_cells)]

    engine = IntegerEngine(vars=cells, vpool=pool)

    # Each digit is used once.
    engine.add_alldifferent(cells)

    # The circles are the corners a, c, f and h, and the squares are b, d, e and g.
    a, b, c, d, e, f, g, h = cells
    # Each square is the sum of the two circles next to it.
    for square, left, right in ((b, a, c), (d, a, f), (e, c, h), (g, f, h)):
        engine.add_linear(square - left - right == 0)

    return engine.clausify(), {"positions": cells}


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
