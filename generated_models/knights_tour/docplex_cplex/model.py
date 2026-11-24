# knights_tour: a CPLEX (Python) model from DCP Rosetta.
# Download the `knights_tour.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python knights_tour.py knights_tour.json

from docplex.mp.model import Model


def create_model(instance):
    """Knight's tour: number the squares of an n-by-n chessboard 0..n*n-1 in the order a knight visits
    them, so that every square is visited exactly once and each move is a knight's move. The tour is
    open: it does not have to return to its starting square."""
    # The eight jumps a knight can make (a property of the piece, not of the instance).
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
    n = instance["n"]  # size of the chessboard
    squares = [(i, j) for i in range(n) for j in range(n)]
    last = n * n - 1  # the number of the last move

    model = Model("knights_tour")

    # x[i][j] is the move number at which the knight stands on square (i, j).
    x = {sq: model.integer_var(0, last, name=f"x_{sq[0]}_{sq[1]}") for sq in squares}

    # The tour is encoded by its moves rather than by a one-hot square-to-number table:
    # jump[a, b] = 1 when the knight goes from square a straight to square b. There is one
    # binary per knight move on the board (576 at n = 10), where the one-hot table would need
    # n**4 binaries and exceed the Community Edition's 1000-variable limit.
    jump = {}
    for (i, j) in squares:
        for di, dj in knight_moves:
            if 0 <= i + di < n and 0 <= j + dj < n:
                jump[(i, j), (i + di, j + dj)] = model.binary_var(name=f"jump_{i}_{j}_{i + di}_{j + dj}")

    # The knight leaves every square at most once and arrives on every square at most once.
    model.add_constraints(model.sum(v for (a, b), v in jump.items() if a == sq) <= 1 for sq in squares)
    model.add_constraints(model.sum(v for (a, b), v in jump.items() if b == sq) <= 1 for sq in squares)

    # Visiting n*n squares takes n*n - 1 moves.
    model.add_constraint(model.sum(jump.values()) == last)

    # A move from a to b means b is visited right after a. The move numbers then rise by one
    # along every chain of moves, so no chain can close into a loop; with n*n - 1 moves and at
    # most one move in and out of each square, the moves form a single path through all
    # squares, numbered 0..n*n-1 in visiting order (hence every square gets a different number).
    for (a, b), v in jump.items():
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
