# kakuro: a CPLEX (Python) model from DCP Rosetta.
# Download the `kakuro.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python kakuro.py kakuro.json

from docplex.mp.model import Model


def create_model(instance):
    """Kakuro: fill the white cells of an n-by-n grid with digits 1..9 so that the digits of every
    segment (a run of cells with a clue) add up to the clue and are all different. Blank cells
    hold 0."""
    n = instance["n"]                # size of the grid
    problem = instance["problem"]    # segments as [sum, [row, col], [row, col], ...], 1-based
    blanks = instance["blanks"]      # blank cells as [row, col], 1-based

    digits = range(1, 10)  # a white cell holds a digit from 1 to 9
    blank = {(r - 1, c - 1) for r, c in blanks}  # the blank cells, 0-based
    segments = [(seg[0], [(r - 1, c - 1) for r, c in seg[1:]]) for seg in problem]  # (clue, its cells), 0-based
    white = {cell for _, cells in segments for cell in cells}  # the cells that belong to a segment

    model = Model("kakuro")

    # has[cell, d] is 1 when the white cell holds digit d; each white cell holds one digit.
    # A cell that is both blank and in a segment cannot be filled, so it gets no digits at all.
    has = {}
    for cell in white:
        options = [] if cell in blank else digits
        for d in options:
            has[cell, d] = model.binary_var(name=f"has_{cell[0]}_{cell[1]}_{d}")
        model.add_constraint(model.sum(has[cell, d] for d in options) == 1)

    # x[i][j] is the number in cell (i, j): 0 in a blank, the digit in a segment cell, and, for a
    # cell that is neither (the statement says nothing about it), left free in 0..9.
    x = []
    for i in range(n):
        row = []
        for j in range(n):
            if (i, j) in white:
                row.append(model.sum(d * has[(i, j), d] for d in digits if ((i, j), d) in has))
            elif (i, j) in blank:
                row.append(0)
            else:
                row.append(model.integer_var(0, 9, name=f"x_{i}_{j}"))
        x.append(row)

    for total, cells in segments:
        # The numbers of the segment add up to its sum.
        model.add_constraint(model.sum(x[r][c] for r, c in cells) == total)
        # All numbers in this segment must be distinct.
        if len(cells) > 1:
            for d in digits:
                model.add_constraint(model.sum(has[cell, d] for cell in cells if (cell, d) in has) <= 1)

    return model, {"x": x}


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
