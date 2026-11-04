# csplib_067_quasigroup_completion: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_067_quasigroup_completion.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_067_quasigroup_completion.py csplib_067_quasigroup_completion.json

from hermax.model import Model


def create_model(instance):
    """Complete a partially filled order-N quasigroup, a Latin square of size N: fill every
    empty cell with a number from 1 to N so that each number occurs exactly once in every
    row and in every column, keeping the numbers that are already given."""
    n = instance["N"]          # N: the size of the square, N rows and N columns
    start = instance["start"]  # start[i][j]: the number given in cell (i, j), 0 if the cell is empty

    m = Model()

    # puzzle[i][j] is the number in cell (i, j), from 1 to N
    puzzle = m.int_matrix("puzzle", n, n, 1, n)

    # Each given number keeps its cell.
    for i in range(n):
        for j in range(n):
            if start[i][j] != 0:
                m &= (puzzle[i][j] == start[i][j])

    # Every row holds each number exactly once.
    for i in range(n):
        m &= puzzle.row(i).all_different()

    # Every column holds each number exactly once.
    for j in range(n):
        m &= puzzle.col(j).all_different()

    return m, {"puzzle": puzzle}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
