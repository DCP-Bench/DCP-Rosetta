# csplib_054_n_queens: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_054_n_queens.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_054_n_queens.py csplib_054_n_queens.json

import mip


def create_model(instance):
    """Place n queens on an n x n chessboard so that no two queens attack each other:
    no two share a row, a column or a diagonal."""
    n = instance["n"]  # the board size, and the number of queens

    cols = range(1, n + 1)  # the columns 1..n

    model = mip.Model(solver_name="CBC")

    # p[i][v] is 1 when the queen in row i stands in column v, and 0 when not
    p = [[model.add_var(f"p_{i}_{v}", var_type=mip.BINARY) for v in cols]
         for i in range(n)]

    # Each row holds exactly one queen.
    for i in range(n):
        model += mip.xsum(p[i][v - 1] for v in cols) == 1

    # Each column holds at most one queen.
    for v in cols:
        model += mip.xsum(p[i][v - 1] for i in range(n)) <= 1

    # Each diagonal running down to the right holds at most one queen.
    for d in range(-n, n + 1):
        terms = [p[i][v - 1] for i in range(n) for v in cols if i - v == d]
        if len(terms) > 1:
            model += mip.xsum(terms) <= 1

    # Each diagonal running down to the left holds at most one queen.
    for s in range(0, 2 * n + 1):
        terms = [p[i][v - 1] for i in range(n) for v in cols if i + v == s]
        if len(terms) > 1:
            model += mip.xsum(terms) <= 1

    # queens[i] is the column, from 1 to n, of the queen in row i.
    queens = []
    for i in range(n):
        q = model.add_var(f"queen_{i}", lb=1, ub=n, var_type=mip.INTEGER)
        model += q == mip.xsum(v * p[i][v - 1] for v in cols)
        queens.append(q)

    return model, {"queens": queens}


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
