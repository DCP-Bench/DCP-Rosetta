# csplib_009_perfect_square_placement: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_009_perfect_square_placement.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_009_perfect_square_placement.py csplib_009_perfect_square_placement.json

import pulp


def create_model(instance):
    """Pack squares of the given integer sides into a bigger square so that no two squares
    overlap and all borders are parallel to the border of the big square. The areas of the
    small squares add up to the area of the big square, so no space is left over."""
    base = instance["base"]    # the side of the big square
    sides = instance["sides"]  # sides[i]: the side of small square i
    n_squares = len(sides)     # the number of small squares

    problem = pulp.LpProblem("perfect_square_placement", pulp.LpMinimize)

    # Whether the near edge of a square, given its flags for the lines, is at or before line u.
    # Lines before the big square are never reached, and lines past the last position always are.
    def edge_reached(flags, u):
        if u < 0:
            return 0
        if u >= len(flags):
            return 1
        return flags[u]

    # Left edge of each square, measured from the left side of the big square. The square
    # stays inside the big square, so the edge is at most base - side.
    x_coords = [pulp.LpVariable(f"x_{i}", 0, base - sides[i], cat="Integer") for i in range(n_squares)]
    # Bottom edge of each square, measured from the bottom of the big square.
    y_coords = [pulp.LpVariable(f"y_{i}", 0, base - sides[i], cat="Integer") for i in range(n_squares)]

    # Two squares that do not overlap are separated: one lies left of, right of, below or above
    # the other. Each separation is chosen by its own binary variable. A separation that is not
    # chosen does not bind, because base is at least the largest distance it has to cover.
    for a in range(n_squares):
        for b in range(a + 1, n_squares):
            separations = []  # the choices of separation for the pair a, b
            for name, first, second, coords in (
                    ("left", a, b, x_coords), ("right", b, a, x_coords),
                    ("below", a, b, y_coords), ("above", b, a, y_coords)):
                holds = pulp.LpVariable(f"{name}_{a}_{b}", cat="Binary")
                problem += (coords[first] + sides[first]
                            <= coords[second] + base * (1 - holds))
                separations.append(holds)
            problem += pulp.lpSum(separations) >= 1

    # The squares fill the big square exactly, so every line across it is crossed by squares
    # whose sides add up to base. Square i crosses line u when its near edge has reached u but
    # not u minus its side. The same holds for the vertical lines (x) and the horizontal lines (y).
    for coords, axis in ((x_coords, "x"), (y_coords, "y")):
        reached = []  # reached[i][u]: whether the near edge of square i is at or before line u
        for i in range(n_squares):
            last = base - sides[i]  # the furthest the near edge of square i can be
            flags = [pulp.LpVariable(f"reached_{axis}_{i}_{u}", cat="Binary") for u in range(last)]
            # Once reached, a line stays reached for every later line.
            for u in range(last - 1):
                problem += flags[u] <= flags[u + 1]
            # The near edge sits at the number of lines it has not yet reached.
            problem += coords[i] == last - pulp.lpSum(flags)
            reached.append(flags)

        for u in range(base):
            problem += pulp.lpSum(
                sides[i] * (edge_reached(reached[i], u) - edge_reached(reached[i], u - sides[i]))
                for i in range(n_squares)) == base

    return problem, {"x_coords": x_coords, "y_coords": y_coords}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
