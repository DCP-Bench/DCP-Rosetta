# csplib_009_perfect_square_placement: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_009_perfect_square_placement.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_009_perfect_square_placement.py csplib_009_perfect_square_placement.json

from pyscipopt import Model


def create_model(instance):
    """Perfect square placement: pack squares with the given integer sides into a
    bigger square so that the squares do not overlap and every square's sides are
    parallel to the big square's sides. The squares' areas add up to the big
    square's area, so the packing leaves no gap. The model states the two
    conditions of the problem: each square lies inside the big square, and no two
    squares overlap. Two cumulative constraints (implied by those conditions) and
    a symmetry-breaking bound are added on top. The output is the lower-left
    corner of each square, with coordinates counted from 0."""
    base = instance["base"]    # side length of the big square
    sides = instance["sides"]  # sides[i]: side length of square i
    n = len(sides)             # number of squares, taken from the data

    model = Model("csplib_009_perfect_square_placement")

    # x[i] and y[i]: the column and the row of the lower-left corner of square i,
    # counted from 0. The square must lie inside the big square, which spans 0 to
    # base, so each corner lies between 0 and base - sides[i].
    x = [model.addVar(f"x_{i}", vtype="I", lb=0, ub=base - sides[i]) for i in range(n)]
    y = [model.addVar(f"y_{i}", vtype="I", lb=0, ub=base - sides[i]) for i in range(n)]

    # For each pair of squares i < j, four binaries choose how the two squares are
    # apart. left[i, j] = 1 selects "square i lies entirely to the left of square j",
    # right[i, j] = 1 selects "square i lies entirely to the right of square j",
    # below[i, j] = 1 selects "square i lies entirely below square j" (smaller y), and
    # above[i, j] = 1 selects "square i lies entirely above square j".
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    left = {p: model.addVar(f"left_{p[0]}_{p[1]}", vtype="B") for p in pairs}
    right = {p: model.addVar(f"right_{p[0]}_{p[1]}", vtype="B") for p in pairs}
    below = {p: model.addVar(f"below_{p[0]}_{p[1]}", vtype="B") for p in pairs}
    above = {p: model.addVar(f"above_{p[0]}_{p[1]}", vtype="B") for p in pairs}

    for i, j in pairs:
        # Each binary switches on its separation: when left[i, j] is 1, the square i
        # must end before square j starts in x, and the other three binaries work
        # the same way. addConsIndicator is used because a constraint that holds only
        # when a binary is 1 needs no big-M constant.
        model.addConsIndicator(x[i] + sides[i] <= x[j], binvar=left[i, j])
        model.addConsIndicator(x[j] + sides[j] <= x[i], binvar=right[i, j])
        model.addConsIndicator(y[i] + sides[i] <= y[j], binvar=below[i, j])
        model.addConsIndicator(y[j] + sides[j] <= y[i], binvar=above[i, j])

        # No overlap: two squares that do not overlap are apart in at least one
        # of the four ways.
        model.addCons(left[i, j] + right[i, j] + below[i, j] + above[i, j] >= 1)

    # Implied constraints (redundant, for propagation only): any vertical line
    # crosses squares whose sides add up to at most base, and likewise any
    # horizontal line. Seen along x, square i is a job that starts at x[i], lasts
    # sides[i] and uses sides[i] of a capacity base; the same along y. They remove
    # no placement; they let the solver prune earlier.
    model.addConsCumulative(x, sides, sides, base, name="cumulative_x")
    model.addConsCumulative(y, sides, sides, base, name="cumulative_y")

    # Symmetry breaking: mirroring a packing left-right or top-bottom gives another
    # packing, so the largest square may be placed with its centre in the lower-left
    # quarter. Its centre is at x + sides/2, which is at most base/2 exactly when
    # 2x <= base - sides; the same holds for y.
    big = max(range(n), key=lambda i: sides[i])
    model.addCons(2 * x[big] <= base - sides[big])
    model.addCons(2 * y[big] <= base - sides[big])

    # Satisfaction problem: no objective is set. Any placement that meets the
    # conditions above and the symmetry-breaking bound is a solution.
    return model, {"x_coords": x, "y_coords": y}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
