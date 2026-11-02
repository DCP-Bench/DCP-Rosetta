# csplib_009_perfect_square_placement: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_009_perfect_square_placement.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_009_perfect_square_placement.py csplib_009_perfect_square_placement.json

from exact import Exact


def create_model(instance):
    """Place squares of given integer sizes inside a bigger square, with sides parallel to it,
    so that no two squares overlap. The squares fill the big square exactly."""
    base = instance["base"]    # side length of the big square
    sides = instance["sides"]  # sides[i]: side length of small square i
    n_squares = len(sides)     # number of small squares

    solver = Exact()

    # x_coords[i] and y_coords[i]: distance from the left and bottom edges of the big square
    # to the lower-left corner of small square i. A square stays inside the big square.
    coords = {"x": [f"x_coords_{i}" for i in range(n_squares)],
              "y": [f"y_coords_{i}" for i in range(n_squares)]}

    # Exact identifies its variables by name.
    # at[axis][i][v] is 1 when square i begins at distance v on that axis.
    at = {axis: [[f"{axis}_coords_{i}_is_{v}" for v in range(base - sides[i] + 1)]
                 for i in range(n_squares)]
          for axis in coords}
    for axis in coords:
        for i in range(n_squares):
            solver.addVariable(coords[axis][i], 0, base - sides[i])
            for name in at[axis][i]:
                solver.addVariable(name, 0, 1)

            # Square i begins at exactly one distance.
            solver.addConstraint([(1, name) for name in at[axis][i]], True, 1, True, 1)

            # The corner coordinate is the distance at which square i begins.
            solver.addConstraint([(v, name) for v, name in enumerate(at[axis][i]) if v]
                                 + [(-1, coords[axis][i])], True, 0, True, 0)

    x_coords, y_coords = coords["x"], coords["y"]

    # Each case says that one square lies entirely to the left of, right of, below or above
    # another. The case variable is 1 exactly when its case holds.
    for a in range(n_squares):
        for b in range(a + 1, n_squares):
            cases = []  # the four cases for squares a and b
            for first, second, axis_coords, label in ((a, b, x_coords, "left"), (b, a, x_coords, "right"),
                                                      (a, b, y_coords, "below"), (b, a, y_coords, "above")):
                case = f"square_{a}_{label}_of_{b}"
                solver.addVariable(case, 0, 1)
                solver.addReification(case, True, [(1, axis_coords[second]), (-1, axis_coords[first])],
                                      sides[first])
                cases.append((1, case))

            # No two squares overlap, so at least one case holds.
            solver.addConstraint(cases, True, 1)

    # The squares fill the big square, so along every column and every row of unit cells the
    # squares crossing it have sides adding up to base. Square i crosses line p when it begins
    # at a distance v with v <= p <= v + sides[i] - 1.
    for axis in coords:
        for p in range(base):
            crossing = [(sides[i], at[axis][i][v]) for i in range(n_squares)
                        for v in range(max(0, p - sides[i] + 1), min(p, base - sides[i]) + 1)]
            solver.addConstraint(crossing, True, base, True, base)

    return solver, {"x_coords": x_coords, "y_coords": y_coords}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
