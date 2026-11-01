# csplib_067_quasigroup_completion: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_067_quasigroup_completion.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_067_quasigroup_completion.py csplib_067_quasigroup_completion.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Complete a partially filled N-by-N table so that each of the numbers 1 to N
    occurs exactly once in every row and every column (a quasigroup, or Latin square)."""
    N = instance["N"]          # order of the quasigroup
    start = instance["start"]  # the given number in each cell, or 0 if the cell is empty

    model = cp_model.CpModel()

    # puzzle[i][j] is the number in the cell at row i, column j.
    # A cell that is already filled can only hold its given number.
    puzzle = []
    for i in range(N):
        row = []
        for j in range(N):
            if start[i][j] != 0:
                row.append(model.new_int_var(start[i][j], start[i][j], f"puzzle_{i}_{j}"))
            else:
                row.append(model.new_int_var(1, N, f"puzzle_{i}_{j}"))
        puzzle.append(row)

    # Each row holds every number once.
    for i in range(N):
        model.add_all_different(puzzle[i])

    # Each column holds every number once.
    for j in range(N):
        model.add_all_different([puzzle[i][j] for i in range(N)])

    return model, {"puzzle": puzzle}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
