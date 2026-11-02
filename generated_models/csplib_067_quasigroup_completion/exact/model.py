# csplib_067_quasigroup_completion: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_067_quasigroup_completion.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_067_quasigroup_completion.py csplib_067_quasigroup_completion.json

from exact import Exact


def create_model(instance):
    """Complete a partly filled table of size n_values by n_values so that each of the
    values 1 to n_values occurs exactly once in every row and every column (a Latin square)."""
    n_values = instance["N"]   # the table is n_values by n_values, and its values are 1 to n_values
    start = instance["start"]  # start[i][j] is the value given in cell (i, j), or 0 when the cell is empty

    solver = Exact()

    # Exact identifies its variables by name.
    # puzzle[i][j] is the value in row i, column j
    puzzle = [[f"puzzle_{i}_{j}" for j in range(n_values)] for i in range(n_values)]
    # holds[i][j][v] is 1 when cell (i, j) has the value v, and 0 otherwise
    holds = [[{} for _ in range(n_values)] for _ in range(n_values)]
    for i in range(n_values):
        for j in range(n_values):
            # a given cell has its value fixed, and an empty cell can take any value
            lo, hi = (start[i][j], start[i][j]) if start[i][j] != 0 else (1, n_values)
            solver.addVariable(puzzle[i][j], lo, hi)
            for v in range(1, n_values + 1):
                holds[i][j][v] = f"holds_{i}_{j}_{v}"
                solver.addVariable(holds[i][j][v], 0, 1)
            # cell (i, j) holds exactly one value
            solver.addConstraint([(1, holds[i][j][v]) for v in range(1, n_values + 1)], True, 1, True, 1)
            # the value in cell (i, j) is the one it holds
            solver.addConstraint([(v, holds[i][j][v]) for v in range(1, n_values + 1)] + [(-1, puzzle[i][j])],
                                 True, 0, True, 0)

    # every row and every column holds each value exactly once
    for v in range(1, n_values + 1):
        for i in range(n_values):
            solver.addConstraint([(1, holds[i][j][v]) for j in range(n_values)], True, 1, True, 1)
            solver.addConstraint([(1, holds[j][i][v]) for j in range(n_values)], True, 1, True, 1)

    return solver, {"puzzle": puzzle}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
