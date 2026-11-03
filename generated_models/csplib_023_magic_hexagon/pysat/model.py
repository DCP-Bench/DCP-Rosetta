# csplib_023_magic_hexagon: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_023_magic_hexagon.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_023_magic_hexagon.py csplib_023_magic_hexagon.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Place the numbers 1 to NUM_CELLS, each once, in the cells of a hexagon with rows of 3, 4,
    5, 4 and 3 cells, so that the numbers along each straight line of cells add up to MAGIC_SUM."""
    n_cells = instance["NUM_CELLS"]    # the number of cells, which is also the largest number to place
    magic_sum = instance["MAGIC_SUM"]  # the total every straight line of cells must reach

    # The cells are numbered row by row from the top:
    #       0  1  2
    #     3  4  5  6
    #   7  8  9 10 11
    #    12 13 14 15
    #      16 17 18
    # The 15 straight lines of cells, as lists of cell numbers.
    LINES = [
        # horizontal rows
        [0, 1, 2], [3, 4, 5, 6], [7, 8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18],
        # lines running from top left to bottom right
        [0, 3, 7], [1, 4, 8, 12], [2, 5, 9, 13, 16], [6, 10, 14, 17], [11, 15, 18],
        # lines running from top right to bottom left
        [2, 6, 11], [1, 5, 10, 15], [0, 4, 9, 14, 18], [3, 8, 13, 17], [7, 12, 16],
    ]

    pool = IDPool()

    # LD[c] is the number written in cell c
    LD = [Integer(f"LD_{c}", 1, n_cells, vpool=pool) for c in range(n_cells)]
    engine = IntegerEngine(vars=LD, vpool=pool)

    # Each number from 1 to NUM_CELLS is written in exactly one cell.
    engine.add_alldifferent(LD)

    # Each straight line of cells adds up to the magic sum.
    for line in LINES:
        engine.add_linear(sum(LD[c] for c in line) == magic_sum)

    return engine.clausify(), {"LD": LD}


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
