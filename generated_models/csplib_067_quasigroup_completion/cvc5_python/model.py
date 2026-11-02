# csplib_067_quasigroup_completion: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_067_quasigroup_completion.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_067_quasigroup_completion.py csplib_067_quasigroup_completion.json

import cvc5.pythonic as c5


def create_model(instance):
    """Complete a partially filled N-by-N table so that each of the numbers 1 to N
    occurs exactly once in every row and every column (a quasigroup, or Latin square)."""
    N = instance["N"]          # order of the quasigroup
    start = instance["start"]  # start[i][j]: the given number in cell (i, j), or 0 if the cell is empty

    # puzzle[i][j] is the number in the cell at row i, column j
    puzzle = [[c5.Int(f"puzzle_{i}_{j}") for j in range(N)] for i in range(N)]

    solver = c5.Solver()

    # Every cell holds a number from 1 to N.
    for row in puzzle:
        for cell in row:
            solver.add(cell >= 1, cell <= N)

    # Each row holds every number once.
    solver.add([c5.Distinct(row) for row in puzzle])

    # Each column holds every number once.
    solver.add([c5.Distinct([row[j] for row in puzzle]) for j in range(N)])

    # The numbers already in the table stay where they are.
    solver.add([puzzle[i][j] == start[i][j] for i in range(N) for j in range(N) if start[i][j] != 0])

    return solver, {"puzzle": puzzle}


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
