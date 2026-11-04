# kakuro: a Choco-solver (Python) model from DCP Rosetta.
# Download the `kakuro.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python kakuro.py kakuro.json

from pychoco.model import Model


def create_model(instance):
    """Insert a digit from 1 to 9 into each white cell of an n by n grid so that the digits
    of each entry add up to its clue and no digit is repeated within an entry. Blank cells
    hold 0."""
    n = instance["n"]  # side of the grid
    blanks = instance["blanks"]  # row and column of each blank cell, numbered from 1 as in the puzzle
    entries = instance["problem"]  # the entries: each clue, followed by the cells it covers

    model = Model()

    # The blank cells, numbered from 0.
    blank_cells = {(row - 1, col - 1) for row, col in blanks}
    # The cells that belong to an entry; these are white.
    white_cells = {(row - 1, col - 1) for _, *cells in entries for row, col in cells}

    # x[r][c] is the digit in row r, column c of the grid.
    x = [
        [
            model.intvar(
                1 if (r, c) in white_cells else 0,
                0 if (r, c) in blank_cells else 9,
                name=f"x_{r}_{c}",
            )
            for c in range(n)
        ]
        for r in range(n)
    ]

    for clue, *cells in entries:
        # The digits in the cells of this entry.
        entry = [x[row - 1][col - 1] for row, col in cells]
        # The digits of the entry add up to its clue.
        model.sum(entry, "=", clue).post()
        # No digit is repeated within the entry.
        model.all_different(entry).post()

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
