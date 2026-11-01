# flow_free_game: a Choco-solver (Python) model from DCP Rosetta.
# Download the `flow_free_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python flow_free_game.py flow_free_game.json

from pychoco.model import Model


def create_model(instance):
    """Flow Free: colour every cell of the board so that the two cells of each colour
    are joined by one pipe of that colour. Pipes never cross, overlap or branch, and
    every cell lies on a pipe."""
    board = instance["board"]  # board[i][j]: the colour given to cell (i, j), or 0 if the cell is empty
    rows, cols = len(board), len(board[0])  # the size of the board
    n_colours = max(max(row) for row in board)  # the colours are numbered 1 to n_colours

    model = Model()

    # B[i][j] is the colour of cell (i, j)
    B = [[model.intvar(1, n_colours, name=f"B_{i}_{j}") for j in range(cols)] for i in range(rows)]

    # same[(a, b)] tells whether the neighbouring cells a and b have the same colour
    same = {}
    for i in range(rows):
        for j in range(cols):
            for k, l in ((i + 1, j), (i, j + 1)):
                if k < rows and l < cols:
                    same[(i, j), (k, l)] = model.arithm(B[i][j], "=", B[k][l]).reify()

    # The neighbours of cell (i, j) that share its colour.
    def same_neighbours(i, j):
        return [flag for (a, c), flag in same.items() if (i, j) in (a, c)]

    for i in range(rows):
        for j in range(cols):
            if board[i][j] != 0:
                # An end cell keeps its given colour and has exactly one neighbour of that colour,
                # because the pipe leaves it in one direction.
                model.arithm(B[i][j], "=", board[i][j]).post()
                model.sum(same_neighbours(i, j), "=", 1).post()
            else:
                # Any other cell lies on a pipe that enters from one neighbour and leaves through
                # another, so exactly two neighbours share its colour.
                model.sum(same_neighbours(i, j), "=", 2).post()

    return model, {"B": B}, None


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
