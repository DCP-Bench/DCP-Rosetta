# minesweeper: a CPLEX (Python) model from DCP Rosetta.
# Download the `minesweeper.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python minesweeper.py minesweeper.json

from docplex.mp.model import Model


def create_model(instance):
    """Minesweeper: decide which unopened cells of the board hold a mine, given that every opened cell
    shows the number of mines among its (up to eight) neighbours."""
    X = instance["X"]              # marker of an unopened cell
    game = instance["game_data"]   # 0-8: number of mines around the cell, X: not opened
    rows, cols = len(game), len(game[0])

    model = Model("minesweeper")

    # mines[r][c] = 1 if cell (r, c) holds a mine
    mines = [[model.binary_var(name=f"mine_{r}_{c}") for c in range(cols)] for r in range(rows)]

    for r in range(rows):
        for c in range(cols):
            val = game[r][c]
            if val == X:
                continue
            # An opened cell cannot be a mine.
            model.add_constraint(mines[r][c] == 0)
            # The number on an opened cell is the number of mines among its neighbours.
            neighbours = [mines[r + a][c + b]
                          for a in (-1, 0, 1) for b in (-1, 0, 1)
                          if (a, b) != (0, 0) and 0 <= r + a < rows and 0 <= c + b < cols]
            model.add_constraint(model.sum(neighbours) == val)

    return model, {"mines": mines}


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
