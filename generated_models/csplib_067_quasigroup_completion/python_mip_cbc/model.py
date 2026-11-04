# csplib_067_quasigroup_completion: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_067_quasigroup_completion.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_067_quasigroup_completion.py csplib_067_quasigroup_completion.json

import mip


def create_model(instance):
    """Complete a partially filled N-by-N table so that each of the numbers 1 to N
    occurs exactly once in every row and every column (a quasigroup, or Latin square)."""
    n = instance["N"]          # order of the quasigroup
    start = instance["start"]  # start[i][j]: the number given in cell (i, j), or 0 if the cell is blank
    values = range(1, n + 1)   # the numbers that can fill a cell

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[i][j][v - 1] is 1 when cell (i, j) holds the number v, and 0 when not
    x = [[[model.add_var(f"x_{i}_{j}_{v}", var_type=mip.BINARY) for v in values]
          for j in range(n)] for i in range(n)]

    # puzzle[i][j] is the number in cell (i, j)
    puzzle = [[model.add_var(f"puzzle_{i}_{j}", lb=1, ub=n, var_type=mip.INTEGER)
               for j in range(n)] for i in range(n)]

    # Each cell holds exactly one number.
    for i in range(n):
        for j in range(n):
            model.add_constr(mip.xsum(x[i][j][v - 1] for v in values) == 1)

    # The number in each cell is the one it holds.
    for i in range(n):
        for j in range(n):
            model.add_constr(puzzle[i][j] == mip.xsum(v * x[i][j][v - 1] for v in values))

    # Each row contains each number exactly once.
    for i in range(n):
        for v in values:
            model.add_constr(mip.xsum(x[i][j][v - 1] for j in range(n)) == 1)

    # Each column contains each number exactly once.
    for j in range(n):
        for v in values:
            model.add_constr(mip.xsum(x[i][j][v - 1] for i in range(n)) == 1)

    # A number given in the table stays in its cell.
    for i in range(n):
        for j in range(n):
            given = start[i][j]
            if given != 0:
                model.add_constr(x[i][j][given - 1] == 1)

    return model, {"puzzle": puzzle}


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
