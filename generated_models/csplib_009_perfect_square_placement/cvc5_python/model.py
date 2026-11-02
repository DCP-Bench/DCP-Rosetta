# csplib_009_perfect_square_placement: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_009_perfect_square_placement.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_009_perfect_square_placement.py csplib_009_perfect_square_placement.json

import cvc5.pythonic as c5


def create_model(instance):
    """Pack squares of given integer sides into a bigger square so that no squares overlap
    and all borders are parallel to the border of the big square."""
    base = instance["base"]    # the side of the big square
    sides = instance["sides"]  # sides[i]: the side of small square i
    n_squares = len(sides)     # the number of small squares

    # x_coords[i] and y_coords[i] are the distances from the lower-left corner of the big square
    # to the left and bottom sides of square i
    x_coords = [c5.Int(f"x_coords_{i}") for i in range(n_squares)]
    y_coords = [c5.Int(f"y_coords_{i}") for i in range(n_squares)]

    # Linear integer logic: cvc5 solves this model much faster than with the default Solver().
    solver = c5.SolverFor("QF_LIA")

    # Every square lies inside the big square.
    for i in range(n_squares):
        solver.add(x_coords[i] >= 0, y_coords[i] >= 0,
                   x_coords[i] <= base - sides[i], y_coords[i] <= base - sides[i])

    # No two squares overlap: for each pair, one of them lies left of, right of, below or above the other.
    for i in range(n_squares):
        for j in range(i + 1, n_squares):
            # left, right, below and above say which of these holds for squares i and j
            left, right, below, above = [c5.Bool(f"{side}_{i}_{j}") for side in ("left", "right", "below", "above")]
            solver.add(
                c5.Or(left, right, below, above),
                c5.Implies(left, x_coords[i] + sides[i] <= x_coords[j]),
                c5.Implies(right, x_coords[j] + sides[j] <= x_coords[i]),
                c5.Implies(below, y_coords[i] + sides[i] <= y_coords[j]),
                c5.Implies(above, y_coords[j] + sides[j] <= y_coords[i]),
            )

    # The areas of the small squares add up to the area of the big square, so no space is left over.
    solver.add(sum(side * side for side in sides) == base * base)

    # Along each horizontal line y = t inside the big square, the squares crossing it have sides
    # that add up to base. The same holds along each vertical line x = t.
    for t in range(base):
        row_cover = []  # the sides of the squares crossing the line y = t
        col_cover = []  # the sides of the squares crossing the line x = t
        for i in range(n_squares):
            side = sides[i]
            # crosses_row and crosses_col say that square i crosses the line y = t, or x = t.
            # A square crosses a line when the line starts at or after the square's lower (left)
            # edge and before its upper (right) edge.
            crosses_row = c5.Bool(f"crosses_row_{i}_{t}")
            crosses_col = c5.Bool(f"crosses_col_{i}_{t}")
            solver.add(
                crosses_row == c5.And(y_coords[i] <= t, y_coords[i] >= t - side + 1),
                crosses_col == c5.And(x_coords[i] <= t, x_coords[i] >= t - side + 1),
            )
            row_cover.append(c5.If(crosses_row, side, 0))
            col_cover.append(c5.If(crosses_col, side, 0))
        solver.add(c5.Sum(row_cover) == base, c5.Sum(col_cover) == base)

    return solver, {"x_coords": x_coords, "y_coords": y_coords}


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
