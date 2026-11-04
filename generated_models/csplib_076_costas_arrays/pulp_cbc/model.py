# csplib_076_costas_arrays: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_076_costas_arrays.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_076_costas_arrays.py csplib_076_costas_arrays.json

import pulp


def create_model(instance):
    """Place n marks on an n-by-n grid, one per row and one per column, so that the
    n(n-1)/2 vectors between pairs of marks are all different (a Costas array)."""
    n = instance["n"]  # size of the grid and number of marks
    columns = range(1, n + 1)

    problem = pulp.LpProblem("costas_array", pulp.LpMinimize)  # satisfaction: no objective

    # put[i][v] is 1 when the mark in row i is in column v, and 0 when not
    put = {i: {v: pulp.LpVariable(f"put_{i}_{v}", cat="Binary") for v in columns} for i in range(n)}

    # costas[i] is the column of the mark in row i, counting columns from 1
    costas = [pulp.LpVariable(f"costas_{i}", 1, n, cat="Integer") for i in range(n)]

    # Each row has one mark, and costas[i] is its column.
    for i in range(n):
        problem += pulp.lpSum(put[i][v] for v in columns) == 1
        problem += costas[i] == pulp.lpSum(v * put[i][v] for v in columns)

    # Each column has one mark.
    for v in columns:
        problem += pulp.lpSum(put[i][v] for i in range(n)) == 1

    # For each row gap gap from 1 to n - 2, the differences between the columns of the marks
    # in rows i and i + gap are all different.
    for gap in range(1, n - 1):
        # pair[(i, u, v)] is 1 when the marks in rows i and i + gap are in columns u and v,
        # and 0 when not. The constraints below make each one 0 or 1.
        pair = {}
        for i in range(n - gap):
            for u in columns:
                for v in columns:
                    pair[(i, u, v)] = pulp.LpVariable(f"pair_{gap}_{i}_{u}_{v}", 0, 1)

            # The pairs that start in column u add up to whether row i has its mark in column u.
            for u in columns:
                problem += pulp.lpSum(pair[(i, u, v)] for v in columns) == put[i][u]

            # The pairs that end in column v add up to whether row i + gap has its mark in column v.
            for v in columns:
                problem += pulp.lpSum(pair[(i, u, v)] for u in columns) == put[i + gap][v]

        # Each difference of columns is taken by at most one pair of rows for this gap.
        for d in range(-(n - 1), n):
            problem += pulp.lpSum(
                pair[(i, u, v)] for i in range(n - gap) for u in columns for v in columns
                if v - u == d) <= 1

    return problem, {"costas": costas}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
