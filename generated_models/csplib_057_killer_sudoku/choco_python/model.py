# csplib_057_killer_sudoku: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_057_killer_sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_057_killer_sudoku.py csplib_057_killer_sudoku.json

from math import isqrt

from pychoco.model import Model


def create_model(instance):
    """Fill an n by n grid with the digits 1 to n so that every row, column and box holds
    each digit once, and every cage holds different digits that add up to its total."""
    n_digits = instance["n"]     # the side of the grid, which is also the largest digit
    cages = instance["problem"]  # each cage has a total and its cells, rows and columns counted from 1
    box = isqrt(n_digits)        # the side of a box (3 for the usual 9 by 9 grid)

    model = Model()

    # x[r][c] is the digit in the cell at row r, column c
    x = [[model.intvar(1, n_digits, name=f"x_{r}_{c}") for c in range(n_digits)] for r in range(n_digits)]

    # Every row holds each digit once.
    for r in range(n_digits):
        model.all_different(x[r]).post()

    # Every column holds each digit once.
    for c in range(n_digits):
        model.all_different([x[r][c] for r in range(n_digits)]).post()

    # Every box holds each digit once.
    for i in range(box):
        for j in range(box):
            model.all_different(
                [x[r][c] for r in range(i * box, (i + 1) * box) for c in range(j * box, (j + 1) * box)]
            ).post()

    # Every cage adds up to its total, with no digit repeated inside it.
    for total, cells in cages:
        cage = [x[r - 1][c - 1] for r, c in cells]  # the digits in this cage
        model.sum(cage, "=", total).post()
        model.all_different(cage).post()

    return model, {"x": x}, None


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
