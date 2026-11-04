# futoshiki: a cvc5 (Python) model from DCP Rosetta.
# Download the `futoshiki.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python futoshiki.py futoshiki.json

import cvc5.pythonic as c5


def create_model(instance):
    """Futoshiki: fill an n-by-n grid with the digits 1 to n so that each row and column holds
    every digit once, the given digits stay in place, and each inequality sign holds. Print the
    completed grid."""
    values = instance["values"]  # the digits given at the start, by row and column; 0 marks an empty cell
    lt = instance["lt"]          # the inequality signs, each as [row, column] of the smaller cell and then of the larger, counted from 1
    n = len(values)              # the grid is n by n

    # grid[r][c] is the digit in row r, column c.
    grid = [[c5.Int(f"grid_{r}_{c}") for c in range(n)] for r in range(n)]

    # Each digit is from 1 to n.
    bounds = [cell >= 1 for row in grid for cell in row] + [cell <= n for row in grid for cell in row]

    # Each row and each column holds every digit once.
    all_different = ([c5.Distinct(row) for row in grid]
                     + [c5.Distinct([grid[r][c] for r in range(n)]) for c in range(n)])

    # The given digits stay in their cells.
    givens = [grid[r][c] == values[r][c] for r in range(n) for c in range(n) if values[r][c] != 0]

    # Each inequality sign holds.
    signs = [grid[r1 - 1][c1 - 1] < grid[r2 - 1][c2 - 1] for r1, c1, r2, c2 in lt]

    solver = c5.Solver()

    solver.add(bounds + all_different + givens + signs)

    return solver, {"grid": grid}


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
