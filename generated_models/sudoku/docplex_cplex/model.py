# sudoku: a CPLEX (Python) model from DCP Rosetta.
# Download the `sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python sudoku.py sudoku.json

from docplex.mp.model import Model


def create_model(instance):
    """Sudoku: fill the 9-by-9 grid, keeping the digits already given, so that every row, column
    and 3-by-3 box holds each digit 1..9 once."""
    # The grid, its boxes and its digits are fixed by the rules of Sudoku.
    SIZE, BOX = 9, 3
    CELLS = range(SIZE)
    DIGITS = range(1, SIZE + 1)
    given = instance["input_grid"]  # given[r][c]: the digit in row r, column c of the input, 0 if empty

    model = Model("sudoku")

    # holds[r, c, d] is 1 when the cell in row r, column c holds digit d.
    holds = model.binary_var_cube(CELLS, CELLS, DIGITS, name="holds")

    # Every cell holds exactly one digit.
    model.add_constraints(model.sum(holds[r, c, d] for d in DIGITS) == 1 for r in CELLS for c in CELLS)

    # A cell filled in the input keeps its digit.
    for r in CELLS:
        for c in CELLS:
            if given[r][c] != 0:
                holds[r, c, given[r][c]].lb = 1

    # Each digit appears once in every row and once in every column.
    model.add_constraints(model.sum(holds[r, c, d] for c in CELLS) == 1 for d in DIGITS for r in CELLS)
    model.add_constraints(model.sum(holds[r, c, d] for r in CELLS) == 1 for d in DIGITS for c in CELLS)

    # Each digit appears once in every 3-by-3 box.
    for d in DIGITS:
        for top in range(0, SIZE, BOX):
            for left in range(0, SIZE, BOX):
                model.add_constraint(model.sum(holds[r, c, d] for r in range(top, top + BOX)
                                               for c in range(left, left + BOX)) == 1,
                                     ctname=f"box_{top}_{left}_{d}")

    # grid[r][c] is the digit in row r, column c of the solved grid.
    grid = [[model.sum(d * holds[r, c, d] for d in DIGITS) for c in CELLS] for r in CELLS]
    return model, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
