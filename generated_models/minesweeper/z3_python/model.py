# minesweeper: a Z3 (Python) model from DCP Rosetta.
# Download the `minesweeper.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python minesweeper.py minesweeper.json

import z3


def create_model(instance):
    """From the numbers on the opened cells of a Minesweeper board, decide which unopened
    cells hold a mine. An opened cell is safe, and its number counts the mines among the
    cells around it, fewer at the edge of the board."""
    unopened = instance["X"]        # the value that marks a cell that is not opened
    game = instance["game_data"]    # game[r][c]: the number on cell (r, c), or the unopened value
    rows, cols = len(game), len(game[0])  # the board height and width

    # mines[r][c] is true when cell (r, c) holds a mine
    mines = [[z3.Bool(f"mine_{r}_{c}") for c in range(cols)] for r in range(rows)]

    solver = z3.Solver()
    for r in range(rows):
        for c in range(cols):
            if game[r][c] != unopened:
                # An opened cell is safe.
                solver.add(z3.Not(mines[r][c]))

                # The cells around (r, c) that are on the board, not counting (r, c) itself.
                neighbours = [
                    mines[a][b]
                    for a in range(max(0, r - 1), min(rows, r + 2))
                    for b in range(max(0, c - 1), min(cols, c + 2))
                    if (a, b) != (r, c)
                ]

                # The number on an opened cell is the count of mines among its neighbours.
                solver.add(z3.PbEq([(m, 1) for m in neighbours], game[r][c]))

    return solver, {"mines": mines}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
