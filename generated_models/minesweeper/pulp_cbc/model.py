# minesweeper: a PuLP (Python) model from DCP Rosetta.
# Download the `minesweeper.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python minesweeper.py minesweeper.json

import pulp


def create_model(instance):
    """From the numbers on the opened cells of a Minesweeper board, decide which
    unopened cells hold a mine. An opened cell shows how many of its neighbouring
    cells are mines."""
    unopened = instance["X"]      # the value that marks a cell that is not opened yet
    game = instance["game_data"]  # game[r][c] is the number on cell (r, c), or the unopened marker
    rows, cols = len(game), len(game[0])  # board height and width

    problem = pulp.LpProblem("minesweeper", pulp.LpMinimize)

    # mines[r][c] is 1 when cell (r, c) holds a mine, and 0 when not
    mines = [[pulp.LpVariable(f"mine_{r}_{c}", cat="Binary") for c in range(cols)]
             for r in range(rows)]

    for r in range(rows):
        for c in range(cols):
            if game[r][c] != unopened:
                # An opened cell holds no mine.
                problem += mines[r][c] == 0
                # The number on the cell is the count of mines among the cells around it.
                # Cells beyond the edge of the board do not count.
                problem += pulp.lpSum(
                    mines[r + a][c + b]
                    for a in (-1, 0, 1) for b in (-1, 0, 1)
                    if (a, b) != (0, 0) and 0 <= r + a < rows and 0 <= c + b < cols
                ) == game[r][c]

    return problem, {"mines": mines}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
