# minesweeper: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `minesweeper.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
# Then run it on the first instance (after `pip install ortools`):
#   python minesweeper.py minesweeper.json

from ortools.sat.python import cp_model


def create_model(instance):
    """From the numbers on the opened cells of a Minesweeper board, decide which
    unopened ('X') cells hold a mine. An opened cell shows how many of its
    neighbouring cells are mines."""
    unopened = instance["X"]      # the value that marks a cell that is not opened yet
    game = instance["game_data"]  # game[r][c]: the number on cell (r, c), or the unopened marker
    rows, cols = len(game), len(game[0])  # board height and width

    model = cp_model.CpModel()

    # mines[r][c] is true when cell (r, c) holds a mine. An opened cell holds none.
    mines = [
        [model.new_int_var(0, 1 if game[r][c] == unopened else 0, f"mine_{r}_{c}") for c in range(cols)]
        for r in range(rows)
    ]

    for r in range(rows):
        for c in range(cols):
            if game[r][c] != unopened:
                # Neighbouring cells beyond the edge of the board do not count.
                model.add(
                    sum(
                        mines[a][b]
                        for a in range(max(0, r - 1), min(rows, r + 2))
                        for b in range(max(0, c - 1), min(cols, c + 2))
                        if (a, b) != (r, c)
                    )
                    == game[r][c]
                )

    return model, {"mines": mines}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
