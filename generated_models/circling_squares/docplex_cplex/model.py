# circling_squares: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python circling_squares.py

from docplex.mp.model import Model


def create_model(instance):
    """Circling the squares (Dudeney): place a different number in each of ten squares around a circle
    so that for any two adjacent squares the sum of the squares of their numbers equals that of the
    two diametrically opposite squares. A = 16, B = 2, F = 8 and G = 14 are given."""
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]  # around the circle
    given = {"A": 16, "B": 2, "F": 8, "G": 14}                   # puzzle givens
    max_number = 99                       # "no number need contain more than two figures"
    numbers = range(1, max_number + 1)    # the numbers are positive, with at most two figures

    model = Model("circling_squares")

    # Squares of numbers are not linear, so each open square picks its number one-hot:
    # pick[x, v] = 1 when square x holds v. The four given squares are constants.
    open_squares = [x for x in names if x not in given]
    pick = {(x, v): model.binary_var(name=f"pick_{x}_{v}") for x in open_squares for v in numbers}
    for x in open_squares:
        model.add_constraint(model.sum(pick[x, v] for v in numbers) == 1)

    # All numbers are different: an open square cannot take a given number, and no number is
    # used by two open squares.
    for v in numbers:
        if v in given.values():
            model.add_constraint(model.sum(pick[x, v] for x in open_squares) == 0)
        else:
            model.add_constraint(model.sum(pick[x, v] for x in open_squares) <= 1)

    def number(x):  # the number in square x, a constant for a given square
        if x in given:
            return given[x]
        return model.sum(v * pick[x, v] for v in numbers)

    def square(x):
        if x in given:
            return model.linear_expr(constant=given[x] ** 2)
        return model.sum(v * v * pick[x, v] for v in numbers)

    # For two adjacent squares, the sum of the squares equals that of the opposite pair:
    # A,B ~ F,G; B,C ~ G,H; C,D ~ H,I; D,E ~ I,K; E,F ~ K,A.
    for x1, x2, y1, y2 in [("A", "B", "F", "G"), ("B", "C", "G", "H"), ("C", "D", "H", "I"),
                           ("D", "E", "I", "K"), ("E", "F", "K", "A")]:
        model.add_constraint(square(x1) + square(x2) == square(y1) + square(y2))

    return model, {x: number(x) for x in names}


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
