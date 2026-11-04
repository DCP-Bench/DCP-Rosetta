# flow_free_game: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `flow_free_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
# Then run it on the first instance (after `pip install ortools`):
#   python flow_free_game.py flow_free_game.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Flow Free: connect the two cells of each colour with a pipe, so that each
    colour forms one pipe and the pipes cover the whole board without crossing or
    overlapping. A pipe is a chain of orthogonally adjacent cells of one colour,
    and its two ends are the cells with that colour given on the board."""
    board = instance["board"]  # board[i][j]: the colour given to cell (i, j), if any
    rows, cols = len(board), len(board[0])  # the board size, in rows and columns
    n_colors = max(max(row) for row in board)  # the colours are numbered 1 to n_colors

    model = cp_model.CpModel()

    # B[i][j] is the colour of cell (i, j)
    B = [[model.new_int_var(1, n_colors, f"B_{i}_{j}") for j in range(cols)] for i in range(rows)]

    # joined[(i, j)] collects the same-colour flags of the neighbours of cell (i, j)
    joined = {(i, j): [] for i in range(rows) for j in range(cols)}
    for i in range(rows):
        for j in range(cols):
            for k, l in ((i + 1, j), (i, j + 1)):
                if k < rows and l < cols:
                    # Neighbouring cells (i, j) and (k, l) have the same colour exactly when same is true.
                    same = model.new_bool_var(f"same_{i}_{j}_{k}_{l}")
                    model.add(B[i][j] == B[k][l]).only_enforce_if(same)
                    model.add(B[i][j] != B[k][l]).only_enforce_if(~same)
                    joined[(i, j)].append(same)
                    joined[(k, l)].append(same)

    for i in range(rows):
        for j in range(cols):
            if board[i][j] != 0:
                # An end cell has its given colour, and its pipe continues into exactly one neighbour.
                model.add(B[i][j] == board[i][j])
                model.add(sum(joined[(i, j)]) == 1)
            else:
                # A cell in the middle of a pipe has exactly two neighbours of its colour: the pipe
                # comes in from one and leaves through the other.
                model.add(sum(joined[(i, j)]) == 2)

    return model, {"B": B}


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
