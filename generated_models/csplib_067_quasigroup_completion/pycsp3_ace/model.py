# csplib_067_quasigroup_completion: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_067_quasigroup_completion.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_067_quasigroup_completion.py csplib_067_quasigroup_completion.json

from pycsp3 import *


def create_model(instance):
    """An order m quasigroup is a Latin square of size m: an m by m multiplication table in which each
    element from 1 to m occurs exactly once in every row and every column. Complete a partially filled
    quasigroup, in which 0 marks an empty cell."""
    # order: the order m of the quasigroup, the side of the table (the instance field N).
    order = instance["N"]

    # start[i][j] is the given value of the cell in row i + 1 and column j + 1, or 0 when the cell is empty.
    start = instance["start"]

    # puzzle[i][j] is the value of the cell in row i + 1 and column j + 1, from 1 to order.
    puzzle = VarArray(size=[order, order], dom=range(1, order + 1))

    satisfy(
        # Each row contains each element from 1 to order exactly once.
        [AllDifferent(puzzle[i]) for i in range(order)],
        # Each column contains each element from 1 to order exactly once.
        [AllDifferent(puzzle[:, j]) for j in range(order)],
        # The given cells keep their values.
        [puzzle[i][j] == start[i][j] for i in range(order) for j in range(order) if start[i][j] != 0],
    )

    return {"puzzle": puzzle}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("puzzle", "=")
        for row in outputs["puzzle"]:
            print(values(row))
    else:
        print("No solution:", status())
