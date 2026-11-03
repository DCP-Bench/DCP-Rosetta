# csplib_009_perfect_square_placement: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_009_perfect_square_placement.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_009_perfect_square_placement.py csplib_009_perfect_square_placement.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Pack squares of given integer sizes into a bigger square so that no squares overlap
    and all borders are parallel to the border of the big square. The areas of the small
    squares add up to the area of the big square, so no space is left over."""
    base = instance["base"]    # the side of the big square
    sides = instance["sides"]  # sides[i]: the side of small square i
    n_squares = len(sides)     # the number of small squares

    model = cp_model.CpModel()

    # x_coords[i] and y_coords[i] are the distances from the lower-left corner of the big square
    # to the left and bottom sides of square i. The square stays inside the big square.
    x_coords = [model.new_int_var(0, base - sides[i], f"x_coords_{i}") for i in range(n_squares)]
    y_coords = [model.new_int_var(0, base - sides[i], f"y_coords_{i}") for i in range(n_squares)]

    # Each square is a box of fixed size, spanning its x and y range.
    x_spans = [model.new_fixed_size_interval_var(x_coords[i], sides[i], f"x_span_{i}") for i in range(n_squares)]
    y_spans = [model.new_fixed_size_interval_var(y_coords[i], sides[i], f"y_span_{i}") for i in range(n_squares)]

    # No two squares overlap: one lies left of, right of, below or above the other.
    model.add_no_overlap_2d(x_spans, y_spans)

    # Squares that cross the same vertical line stack up inside the big square, so their sides
    # add up to at most base. The same holds for horizontal lines.
    model.add_cumulative(x_spans, sides, base)
    model.add_cumulative(y_spans, sides, base)

    return model, {"x_coords": x_coords, "y_coords": y_coords}


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
