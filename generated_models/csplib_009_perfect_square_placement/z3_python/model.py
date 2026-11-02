# csplib_009_perfect_square_placement: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_009_perfect_square_placement.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_009_perfect_square_placement.py csplib_009_perfect_square_placement.json

import z3


def create_model(instance):
    """Pack squares of given integer sizes into a bigger square so that no squares overlap
    and all borders are parallel to the border of the big square. The areas of the small
    squares add up to the area of the big square, so no space is left over."""
    base = instance["base"]    # the side of the big square
    sides = instance["sides"]  # sides[i]: the side of small square i
    n = len(sides)             # the number of small squares

    # (x_coords[i], y_coords[i]) is the lower-left corner of square i, measured from the lower-left corner of the big square.
    x_coords = [z3.Int(f"x_coords_{i}") for i in range(n)]
    y_coords = [z3.Int(f"y_coords_{i}") for i in range(n)]

    solver = z3.Solver()

    # Every square lies inside the big square.
    for i in range(n):
        solver.add(x_coords[i] >= 0, x_coords[i] + sides[i] <= base,
                   y_coords[i] >= 0, y_coords[i] + sides[i] <= base)

    # No two squares overlap: one lies left of, right of, below or above the other.
    for a in range(n):
        for b in range(a + 1, n):
            solver.add(z3.Or(
                x_coords[a] + sides[a] <= x_coords[b],
                x_coords[b] + sides[b] <= x_coords[a],
                y_coords[a] + sides[a] <= y_coords[b],
                y_coords[b] + sides[b] <= y_coords[a]))

    # crosses_column[i] is true when square i covers the unit-wide column at position line;
    # crosses_row[i] does the same for the unit-wide row at position line.
    # Every unit-wide column and every unit-wide row of the big square is crossed by squares
    # whose sides add up to exactly base.
    for line in range(base):
        crosses_column = [z3.And(x_coords[i] <= line, line < x_coords[i] + sides[i]) for i in range(n)]
        crosses_row = [z3.And(y_coords[i] <= line, line < y_coords[i] + sides[i]) for i in range(n)]
        solver.add(z3.PbEq([(crosses_column[i], sides[i]) for i in range(n)], base))
        solver.add(z3.PbEq([(crosses_row[i], sides[i]) for i in range(n)], base))

    return solver, {"x_coords": x_coords, "y_coords": y_coords}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
