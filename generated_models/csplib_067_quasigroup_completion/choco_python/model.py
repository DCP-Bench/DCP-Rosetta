# csplib_067_quasigroup_completion: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_067_quasigroup_completion.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_067_quasigroup_completion.py csplib_067_quasigroup_completion.json

from pychoco.model import Model


def create_model(instance):
    """Complete a partially filled N-by-N table so that each of the numbers 1 to N
    occurs exactly once in every row and every column (a quasigroup, or Latin square)."""
    n = instance["N"]          # order of the quasigroup
    start = instance["start"]  # the given number in each cell, 0 for an empty cell

    model = Model()

    # puzzle[i][j] is the number in the cell at row i, column j.
    # A cell that is already filled can only hold its given number.
    puzzle = []
    for i in range(n):
        row = []
        for j in range(n):
            if start[i][j] != 0:
                row.append(model.intvar(start[i][j], start[i][j], name=f"puzzle_{i}_{j}"))
            else:
                row.append(model.intvar(1, n, name=f"puzzle_{i}_{j}"))
        puzzle.append(row)

    # Each row holds every number once.
    for i in range(n):
        model.all_different(puzzle[i]).post()

    # Each column holds every number once.
    for j in range(n):
        model.all_different([puzzle[i][j] for i in range(n)]).post()

    return model, {"puzzle": puzzle}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
