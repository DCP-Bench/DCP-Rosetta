# csplib_023_magic_hexagon: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_023_magic_hexagon.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_023_magic_hexagon.py csplib_023_magic_hexagon.json

import cvc5.pythonic as c5


def create_model(instance):
    """Place the numbers 1 to n_cells, each once, in the cells of a hexagon so that each of its
    15 straight lines of cells adds up to magic_sum."""
    n_cells = instance["NUM_CELLS"]  # the numbers 1 to n_cells are placed, one per cell
    magic_sum = instance["MAGIC_SUM"]  # the sum every straight line of cells must reach

    # The number written in each cell of the hexagon, cells A to S.
    cells = [c5.Int(name) for name in "A B C D E F G H I J K L M N O P Q R S".split()]
    A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S = cells

    solver = c5.Solver()

    # Each cell holds a whole number from 1 to n_cells.
    for c in cells:
        solver.add(c >= 1, c <= n_cells)

    # The numbers are all different.
    solver.add(c5.Distinct(cells))

    # Together the 19 cells hold 1 to n_cells, so they add up to 1 + 2 + ... + n_cells.
    solver.add(c5.Sum(cells) == n_cells * (n_cells + 1) // 2)

    # The three horizontal rows of the hexagon, top to bottom.
    rows = [
        [A, B, C],
        [D, E, F, G],
        [H, I, J, K, L],
        [M, N, O, P],
        [Q, R, S],
    ]
    # The five lines running from top left to bottom right.
    down_right = [
        [A, E, J, O, S],
        [B, F, K, P],
        [C, G, L],
        [D, I, N, R],
        [H, M, Q],
    ]
    # The five lines running from top right to bottom left.
    down_left = [
        [C, F, J, N, Q],
        [B, E, I, M],
        [A, D, H],
        [G, K, O, R],
        [L, P, S],
    ]

    # Each of the 15 straight lines of cells adds up to magic_sum.
    solver.add([c5.Sum(line) == magic_sum for line in rows + down_right + down_left])

    return solver, {"LD": cells}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
