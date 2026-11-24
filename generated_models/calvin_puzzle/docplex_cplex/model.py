# calvin_puzzle: a CPLEX (Python) model from DCP Rosetta.
# Download the `calvin_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python calvin_puzzle.py calvin_puzzle.json

from docplex.mp.model import Model


def create_model(instance):
    """Calvin's puzzle: fill an n-by-n grid with the numbers 1..n^2 so that each next number is placed
    either three squares away horizontally or vertically (a two-square gap), or two squares away
    diagonally (a one-square gap) from the previous number."""
    # The moves from one number to the next: three squares along a row or column, or two
    # squares along a diagonal.
    STEPS = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]
    n = instance["n"]  # size of the grid
    squares = [(i, j) for i in range(n) for j in range(n)]
    last = n * n  # the numbers 1..last, one on each square

    model = Model("calvin_puzzle")

    # x[i][j] is the number placed on square (i, j).
    x = {sq: model.integer_var(1, last, name=f"x_{sq[0]}_{sq[1]}") for sq in squares}

    # The filling order is encoded by its steps rather than by a one-hot square-to-number table:
    # step[a, b] = 1 when the number after the one on square a is placed on square b. There is
    # one binary per allowed step on the board, where a one-hot table needs n^4 binaries.
    step = {}
    for (i, j) in squares:
        for di, dj in STEPS:
            if 0 <= i + di < n and 0 <= j + dj < n:
                step[(i, j), (i + di, j + dj)] = model.binary_var(name=f"step_{i}_{j}_{i + di}_{j + dj}")

    # Every square is followed by at most one square and preceded by at most one square.
    model.add_constraints(model.sum(v for (a, b), v in step.items() if a == sq) <= 1 for sq in squares)
    model.add_constraints(model.sum(v for (a, b), v in step.items() if b == sq) <= 1 for sq in squares)

    # Filling n^2 squares takes n^2 - 1 steps.
    model.add_constraint(model.sum(step.values()) == last - 1)

    # A step from a to b means b holds the number after a's. Numbers then rise by one along
    # every chain of steps, so no chain closes into a loop; with n^2 - 1 steps and at most one
    # step in and out of each square, the steps form one path through all squares, numbered
    # 1..n^2 in order, so every square gets a different number.
    for (a, b), v in step.items():
        model.add_indicator(v, x[b] == x[a] + 1)

    return model, {"x": [[x[i, j] for j in range(n)] for i in range(n)]}


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
