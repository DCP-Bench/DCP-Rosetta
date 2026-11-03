# calvin_puzzle: a Python-MIP (Python) model from DCP Rosetta.
# Download the `calvin_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python calvin_puzzle.py calvin_puzzle.json

import mip


def create_model(instance):
    """Fill an n by n grid with the numbers 1 to n^2 in sequence. The next number goes either
    exactly three squares away horizontally or vertically, or exactly two squares away
    diagonally from the previous one."""
    n = instance["n"]  # the grid has n rows and n columns
    n_cells = n * n    # the number of squares, which is also the largest number

    model = mip.Model(solver_name="CBC")

    # The squares of the grid, as (row, column) pairs.
    cells = [(i, j) for i in range(n) for j in range(n)]

    # The moves allowed from one square to the next, as (row change, column change): three
    # squares along a row or column, or two squares along a diagonal.
    moves = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]

    # p[v][i][j] is 1 when the number v + 1 is written in row i, column j.
    p = [
        [[model.add_var(f"p_{v}_{i}_{j}", var_type=mip.BINARY) for j in range(n)] for i in range(n)]
        for v in range(n_cells)
    ]
    # x[i][j] is the number written in row i, column j.
    x = [
        [model.add_var(f"x_{i}_{j}", lb=1, ub=n_cells, var_type=mip.INTEGER) for j in range(n)]
        for i in range(n)
    ]

    # Each square holds exactly one number, and x shows that number.
    for i, j in cells:
        model += mip.xsum(p[v][i][j] for v in range(n_cells)) == 1
        model += x[i][j] == mip.xsum((v + 1) * p[v][i][j] for v in range(n_cells))

    # Each number from 1 to n^2 is written in exactly one square.
    for v in range(n_cells):
        model += mip.xsum(p[v][i][j] for i, j in cells) == 1

    # The number k + 2 is reached from the number k + 1 by one allowed move. q[k][i][j][o] is 1
    # when the number k + 1 is in square (i, j) and the number k + 2 is reached from it by move o.
    for k in range(n_cells - 1):
        # landing[i][j] lists the moves that end on square (i, j).
        landing = [[[] for _ in range(n)] for _ in range(n)]
        for i, j in cells:
            # qs lists the moves from square (i, j) that stay on the grid.
            qs = []
            for o, (a, b) in enumerate(moves):
                ti, tj = i + a, j + b
                if 0 <= ti < n and 0 <= tj < n:
                    q = model.add_var(f"q_{k}_{i}_{j}_{o}", var_type=mip.BINARY)
                    model += q <= p[k][i][j]
                    model += q <= p[k + 1][ti][tj]
                    qs.append(q)
                    landing[ti][tj].append(q)
            # The number k + 1 makes exactly one move if it is in square (i, j).
            model += mip.xsum(qs) == p[k][i][j]
        # The number k + 2 is reached by exactly one move, from the number k + 1.
        for ti, tj in cells:
            model += mip.xsum(landing[ti][tj]) == p[k + 1][ti][tj]

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
