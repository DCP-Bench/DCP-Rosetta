# csplib_067_quasigroup_completion: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_067_quasigroup_completion.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_067_quasigroup_completion.py csplib_067_quasigroup_completion.json

import z3


def create_model(instance):
    """Complete a partially filled N-by-N table so that each of the numbers 1 to N
    occurs exactly once in every row and every column (a quasigroup, or Latin square)."""
    N = instance["N"]          # order of the quasigroup
    start = instance["start"]  # start[i][j] is the number given in cell (i, j), 0 if the cell is empty

    # puzzle[i][j] is the number in the cell at row i, column j
    puzzle = [[z3.Int(f"puzzle_{i}_{j}") for j in range(N)] for i in range(N)]

    solver = z3.Solver()

    # Every cell holds a number from 1 to N.
    solver.add([z3.And(1 <= puzzle[i][j], puzzle[i][j] <= N) for i in range(N) for j in range(N)])

    # A given cell keeps its number.
    solver.add([puzzle[i][j] == start[i][j] for i in range(N) for j in range(N) if start[i][j] != 0])

    # Each row holds every number once.
    solver.add([z3.Distinct(row) for row in puzzle])

    # Each column holds every number once.
    solver.add([z3.Distinct([puzzle[i][j] for i in range(N)]) for j in range(N)])

    return solver, {"puzzle": puzzle}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
