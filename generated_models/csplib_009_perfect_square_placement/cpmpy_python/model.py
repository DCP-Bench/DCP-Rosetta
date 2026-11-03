# csplib_009_perfect_square_placement: a CPMpy model from DCP Rosetta.
# Download the `csplib_009_perfect_square_placement.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_009_perfect_square_placement.py csplib_009_perfect_square_placement.json

import cpmpy as cp


def create_model(instance):
    """Pack squares of given integer sizes into a bigger square so that no squares overlap
    and all borders are parallel to the border of the big square. The areas of the small
    squares add up to the area of the big square, so no space is left over."""
    base = instance["base"]    # the side of the big square
    sides = instance["sides"]  # sides[i]: the side of small square i
    n = len(sides)

    # (x_coords[i], y_coords[i]) is the lower-left corner of square i, counted from 0.
    # A square of side s starts at most base - s from the origin, which keeps it inside
    # the big square.
    x_coords = cp.cpm_array([cp.intvar(0, base - sides[i], name=f"x_coords[{i}]") for i in range(n)])
    y_coords = cp.cpm_array([cp.intvar(0, base - sides[i], name=f"y_coords[{i}]") for i in range(n)])

    model = cp.Model()

    # No two squares overlap: one lies left of, right of, below or above the other.
    for a in range(n):
        for b in range(a + 1, n):
            model.add((x_coords[a] + sides[a] <= x_coords[b])
                      | (x_coords[b] + sides[b] <= x_coords[a])
                      | (y_coords[a] + sides[a] <= y_coords[b])
                      | (y_coords[b] + sides[b] <= y_coords[a]))

    # Implied constraints that help the search: the squares crossing any column (row) are
    # stacked, so their sides add up to at most the base. Non-overlap already implies this;
    # stating it lets the solver reason about total extent, as with a cumulative resource
    # of capacity base.
    model.add(cp.Cumulative(x_coords, sides, demand=sides, capacity=base))
    model.add(cp.Cumulative(y_coords, sides, demand=sides, capacity=base))

    return model, {"x_coords": x_coords, "y_coords": y_coords}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
