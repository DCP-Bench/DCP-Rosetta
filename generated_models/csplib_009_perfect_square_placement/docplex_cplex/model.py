# csplib_009_perfect_square_placement: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_009_perfect_square_placement.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_009_perfect_square_placement.py csplib_009_perfect_square_placement.json

from docplex.mp.model import Model


def create_model(instance):
    """Perfect square placement: pack squares with given integer sizes into a bigger square so
    that no squares overlap and all square borders are parallel to the border of the big square.
    The squares' areas add up to the big square's, so there is no spare room."""
    base = instance["base"]    # side length of the big square
    sides = instance["sides"]  # side lengths of the small squares
    n = len(sides)  # number of small squares

    model = Model("perfect_square_placement")

    # x_coords[i], y_coords[i] is the lower-left corner of square i. The bounds keep the
    # square inside the big square: the corner is at most base - side.
    x_coords = [model.integer_var(0, base - sides[i], name=f"x_{i}") for i in range(n)]
    y_coords = [model.integer_var(0, base - sides[i], name=f"y_{i}") for i in range(n)]

    # No two squares overlap: for each pair, one is left of, right of, below or above the
    # other. Two binaries p, q choose which of these four holds, as in the table
    #     (p, q) = (0, 0): a left of b      (1, 0): b left of a
    #              (0, 1): a below b        (1, 1): b below a
    # Each row below is relaxed by base * (a factor that is at least 1) except for its own
    # choice, where the factor is 0. base is the largest the left-hand side can be, so a
    # relaxed row never binds. This takes four rows and two binaries per pair, where one
    # binary per relation would also need a row saying that one of them holds.
    for a in range(n):
        for b in range(a + 1, n):
            p = model.binary_var(name=f"p_{a}_{b}")
            q = model.binary_var(name=f"q_{a}_{b}")
            model.add_constraint(x_coords[a] + sides[a] - x_coords[b] <= base * (p + q))
            model.add_constraint(x_coords[b] + sides[b] - x_coords[a] <= base * (1 - p + q))
            model.add_constraint(y_coords[a] + sides[a] - y_coords[b] <= base * (1 + p - q))
            model.add_constraint(y_coords[b] + sides[b] - y_coords[a] <= base * (2 - p - q))

    return model, {"x_coords": x_coords, "y_coords": y_coords}


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
