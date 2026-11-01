# minesweeper: a Choco-solver (Python) model from DCP Rosetta.
# Download the `minesweeper.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python minesweeper.py minesweeper.json

from pychoco.model import Model


def create_model(instance):
    """From the numbers on the opened cells of a Minesweeper board, decide which
    unopened cells hide a mine. An opened cell shows how many of its neighbouring
    cells are mines."""
    unopened = instance["X"]      # the value that marks a cell that is not opened
    game = instance["game_data"]  # game[r][c]: what is shown on cell (r, c)
    rows, cols = len(game), len(game[0])  # the board height and width

    model = Model()

    # mines[r][c] is true when cell (r, c) holds a mine
    mines = [[model.boolvar(name=f"mines_{r}_{c}") for c in range(cols)] for r in range(rows)]

    for r in range(rows):
        for c in range(cols):
            if game[r][c] != unopened:
                # An opened cell holds no mine.
                model.arithm(mines[r][c], "=", 0).post()

                # The cells around (r, c), fewer at the edge of the board.
                neighbours = [mines[r + a][c + b]
                              for a in (-1, 0, 1) for b in (-1, 0, 1)
                              if (a, b) != (0, 0) and 0 <= r + a < rows and 0 <= c + b < cols]
                # The number on an opened cell is the count of mines around it.
                model.sum(neighbours, "=", game[r][c]).post()

    return model, {"mines": mines}, None


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
