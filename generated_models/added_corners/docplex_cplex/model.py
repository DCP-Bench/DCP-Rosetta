# added_corners: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python added_corners.py

from docplex.mp.model import Model


def create_model(instance):
    """Added corners: place the digits 1..8 in the four corner circles and four side squares of a
    3-by-3 frame so that every square holds the sum of the two circles next to it."""
    n = 8  # the digits 1..8, one per position (puzzle constant)
    digits = range(1, n + 1)
    places = range(n)

    model = Model("added_corners")

    # put[k, v] is 1 when position k holds digit v
    put = {(k, v): model.binary_var(name=f"put_{k}_{v}") for k in places for v in digits}

    # Every position holds one digit, and every digit is used exactly once.
    model.add_constraints(model.sum(put[k, v] for v in digits) == 1 for k in places)
    model.add_constraints(model.sum(put[k, v] for k in places) == 1 for v in digits)

    def value(k):  # the digit in position k
        return model.sum(v * put[k, v] for v in digits)

    # The positions, read like a book:  a b c
    #                                   d   e
    #                                   f g h
    # The corners (circles) are a, c, f, h; the middles of the sides (squares) are b, d, e, g.
    a, b, c, d, e, f, g, h = places

    # Each square equals the sum of its two adjoining corner circles.
    model.add_constraint(value(b) == value(a) + value(c))  # top side
    model.add_constraint(value(d) == value(a) + value(f))  # left side
    model.add_constraint(value(e) == value(c) + value(h))  # right side
    model.add_constraint(value(g) == value(f) + value(h))  # bottom side

    return model, {"positions": [value(k) for k in places]}


if __name__ == "__main__":
    model, outputs = create_model({})
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
