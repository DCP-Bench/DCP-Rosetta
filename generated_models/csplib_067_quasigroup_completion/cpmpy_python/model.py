# csplib_067_quasigroup_completion: a CPMpy model from DCP Rosetta.
# Download the `csplib_067_quasigroup_completion.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_067_quasigroup_completion.py csplib_067_quasigroup_completion.json

import cpmpy as cp


def create_model(instance):
    """Complete a partially filled N-by-N table so that each of the numbers 1 to N
    occurs exactly once in every row and every column (a quasigroup, or Latin square)."""
    N = instance["N"]          # order of the quasigroup
    start = instance["start"]  # start[i][j]: the given value of cell (i, j), or 0 if it is empty

    # puzzle[i][j] is the number in the cell at row i, column j
    puzzle = cp.intvar(1, N, shape=(N, N), name="puzzle")

    model = cp.Model()

    # The cells that are already filled keep their given value.
    for i in range(N):
        for j in range(N):
            if start[i][j] != 0:
                model.add(puzzle[i, j] == start[i][j])

    # Each row holds every number once.
    for i in range(N):
        model.add(cp.AllDifferent(puzzle[i, :]))

    # Each column holds every number once.
    for j in range(N):
        model.add(cp.AllDifferent(puzzle[:, j]))

    return model, {"puzzle": puzzle}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
