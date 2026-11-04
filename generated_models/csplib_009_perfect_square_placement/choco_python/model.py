# csplib_009_perfect_square_placement: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_009_perfect_square_placement.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_009_perfect_square_placement.py csplib_009_perfect_square_placement.json

from pychoco.model import Model


def create_model(instance):
    """Pack squares of given integer sizes into a bigger square so that no squares overlap
    and all borders are parallel to the border of the big square. The areas of the small
    squares add up to the area of the big square, so no space is left over."""
    base = instance["base"]    # the side of the big square
    sides = instance["sides"]  # sides[i]: the side of small square i
    n_squares = len(sides)     # the number of small squares

    model = Model()

    # x_coords[i], y_coords[i]: the lower-left corner of square i, counted from the corner of the big square.
    # The square stays inside the big square.
    x_coords = [model.intvar(0, base - sides[i], name=f"x_coords_{i}") for i in range(n_squares)]
    y_coords = [model.intvar(0, base - sides[i], name=f"y_coords_{i}") for i in range(n_squares)]

    # The width and the height of each square, fixed to its given side.
    widths = [model.intvar(s, s) for s in sides]
    heights = [model.intvar(s, s) for s in sides]

    # No two squares overlap. Squares that cross the same line also stack within the big square.
    model.diff_n(x_coords, y_coords, widths, heights, add_cumulative_reasoning=True).post()

    return model, {"x_coords": x_coords, "y_coords": y_coords}, None


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
