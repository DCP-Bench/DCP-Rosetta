# csplib_067_quasigroup_completion: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_067_quasigroup_completion.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_067_quasigroup_completion.py csplib_067_quasigroup_completion.json

import pulp


def create_model(instance):
    """Complete a partly filled N-by-N table so that each of the numbers 1 to N occurs
    exactly once in every row and every column (a quasigroup, or Latin square)."""
    n = instance["N"]          # order of the quasigroup: the table is n by n
    start = instance["start"]  # start[i][j]: the number already written in cell (i, j), or 0 for an empty cell

    problem = pulp.LpProblem("quasigroup_completion", pulp.LpMinimize)  # satisfaction: no objective

    # put[i][j][v] is 1 when cell (i, j) holds the number v + 1, and 0 when not
    put = [[[pulp.LpVariable(f"put_{i}_{j}_{v}", cat="Binary") for v in range(n)]
            for j in range(n)] for i in range(n)]

    # puzzle[i][j] is the number in cell (i, j); a cell that is already filled keeps its number
    puzzle = [[pulp.LpVariable(f"puzzle_{i}_{j}", start[i][j] or 1, start[i][j] or n, cat="Integer")
               for j in range(n)] for i in range(n)]

    # Every cell holds exactly one number.
    for i in range(n):
        for j in range(n):
            problem += pulp.lpSum(put[i][j]) == 1

    # The number in each cell is the one it holds.
    for i in range(n):
        for j in range(n):
            problem += puzzle[i][j] == pulp.lpSum((v + 1) * put[i][j][v] for v in range(n))

    # Each number occurs once in every row.
    for v in range(n):
        for i in range(n):
            problem += pulp.lpSum(put[i][j][v] for j in range(n)) == 1

    # Each number occurs once in every column.
    for v in range(n):
        for j in range(n):
            problem += pulp.lpSum(put[i][j][v] for i in range(n)) == 1

    return problem, {"puzzle": puzzle}


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
