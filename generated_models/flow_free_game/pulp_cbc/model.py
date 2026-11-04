# flow_free_game: a PuLP (Python) model from DCP Rosetta.
# Download the `flow_free_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python flow_free_game.py flow_free_game.json

import pulp


def create_model(instance):
    """Flow Free: connect the matching colored endpoints on a board with pipes, so that the
    pipes cover every cell and never cross. Each color is one pipe, running from one of its
    endpoints to the other."""
    board = instance["board"]  # board[i][j]: the color of cell (i, j), or 0 for an empty cell
    rows, cols = len(board), len(board[0])  # the board size, in rows and columns
    cells = [(i, j) for i in range(rows) for j in range(cols)]  # every cell of the board
    colors = range(1, 11)  # colors 1 to 10; the board uses only the first few

    # The problem has no objective: any board that follows the rules is a solution.
    problem = pulp.LpProblem("flow_free_game", pulp.LpMinimize)

    # has_color[cell][c] is 1 when the cell has color c, and 0 when not
    has_color = {cell: {c: pulp.LpVariable(f"has_color_{cell[0]}_{cell[1]}_{c}", cat="Binary")
                        for c in colors} for cell in cells}

    # Each cell gets exactly one color.
    for cell in cells:
        problem += pulp.lpSum(has_color[cell].values()) == 1

    # The given endpoints keep their color.
    for (i, j) in cells:
        if board[i][j] != 0:
            problem += has_color[(i, j)][board[i][j]] == 1

    # same_color[u, v] is 1 when the neighboring cells u and v have the same color. For each
    # color c, flag[c] is 1 exactly when both cells have color c. A cell has one color, so at
    # most one flag is 1, and same_color is the sum of the flags.
    same_color = {}
    for (i, j) in cells:
        for (k, l) in ((i + 1, j), (i, j + 1)):
            if k < rows and l < cols:
                u, v = (i, j), (k, l)
                flags = []
                for c in colors:
                    flag = pulp.LpVariable(f"flag_{i}_{j}_{k}_{l}_{c}", cat="Binary")
                    problem += flag <= has_color[u][c]
                    problem += flag <= has_color[v][c]
                    problem += flag >= has_color[u][c] + has_color[v][c] - 1
                    flags.append(flag)
                same_color[u, v] = same_color[v, u] = pulp.lpSum(flags)

    # An endpoint joins exactly one neighbor of its color, and every other cell joins two.
    for (i, j) in cells:
        neighbors = [(k, l) for (k, l) in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                     if 0 <= k < rows and 0 <= l < cols]
        joined = pulp.lpSum(same_color[(i, j), nb] for nb in neighbors)
        problem += joined == (1 if board[i][j] != 0 else 2)

    # B[i][j]: the color of cell (i, j)
    B = [[pulp.lpSum(c * has_color[(i, j)][c] for c in colors) for j in range(cols)]
         for i in range(rows)]

    return problem, {"B": B}


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
