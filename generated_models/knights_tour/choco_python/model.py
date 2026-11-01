# knights_tour: a Choco-solver (Python) model from DCP Rosetta.
# Download the `knights_tour.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python knights_tour.py knights_tour.json

from pychoco.model import Model


def create_model(instance):
    """A knight visits every square of an n by n chessboard exactly once, without
    returning to the starting square. The tour numbers the squares by move, from 0."""
    n = instance["n"]  # the board is n by n
    size = n * n       # the number of squares, which is also the number of moves

    model = Model()

    # The move at which the knight visits each square, with the squares numbered row by row.
    x_flat = [model.intvar(0, size - 1, name=f"x_{s}") for s in range(size)]
    # where[k] is the square the knight visits at move k, the reverse of x_flat.
    where = [model.intvar(0, size - 1, name=f"where_{k}") for k in range(size)]

    # Each square is visited at a different move, and the two lists describe the same tour.
    model.all_different(x_flat).post()
    model.inverse_channeling(x_flat, where).post()

    # The eight knight moves as (row change, column change).
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

    # Pairs of squares on the board that a knight's move apart.
    knight_moves_apart = []
    for i in range(n):
        for j in range(n):
            for di, dj in knight_moves:
                if 0 <= i + di < n and 0 <= j + dj < n:
                    knight_moves_apart.append([i * n + j, (i + di) * n + (j + dj)])

    # The square of move k + 1 is a knight's move away from the square of move k.
    for k in range(size - 1):
        model.table([where[k], where[k + 1]], knight_moves_apart).post()

    # The same move numbers as an n by n grid, x[i][j] for the square (i, j).
    x = [[x_flat[i * n + j] for j in range(n)] for i in range(n)]
    return model, {"x": x}, None


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
