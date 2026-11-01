# csplib_057_killer_sudoku: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_057_killer_sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_057_killer_sudoku.py csplib_057_killer_sudoku.json

from math import isqrt

from ortools.sat.python import cp_model


def create_model(instance):
    """Fill an n-by-n grid with the numbers 1 to n so that every row, column and box
    holds each number once, and every cage (a group of cells) holds distinct numbers
    adding up to the small number printed in its corner."""
    n = instance["n"]            # side of the grid
    cages = instance["problem"]  # the total of each cage and its cells, counted from 1
    box = isqrt(n)               # side of a box (3 for the usual 9x9 grid)

    model = cp_model.CpModel()

    # x[r][c] is the number written in the cell at row r, column c
    x = [[model.new_int_var(1, n, f"x_{r}_{c}") for c in range(n)] for r in range(n)]

    # Every row holds each number once.
    for r in range(n):
        model.add_all_different(x[r])

    # Every column holds each number once.
    for c in range(n):
        model.add_all_different([x[r][c] for r in range(n)])

    # Every box holds each number once.
    for i in range(box):
        for j in range(box):
            model.add_all_different(
                [x[r][c] for r in range(i * box, (i + 1) * box) for c in range(j * box, (j + 1) * box)]
            )

    # Every cage adds up to its total, and no number appears twice inside a cage.
    for total, cells in cages:
        # the numbers written in the cells of this cage
        cage = [x[r - 1][c - 1] for r, c in cells]
        model.add(sum(cage) == total)
        model.add_all_different(cage)

    return model, {"x": x}


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
