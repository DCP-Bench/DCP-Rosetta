# flow_free_game: a Gurobi (Python) model from DCP Rosetta.
# Download the `flow_free_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python flow_free_game.py flow_free_game.json

import gurobipy as gp
from gurobipy import GRB

def create_model(instance):
    """Flow Free: colour every cell of the board so that each pair of equal endpoints is joined
    by a pipe, the pipes covering the whole board and never crossing or overlapping."""
    board = instance["board"]  # board[i][j]: the colour of the endpoint in row i, column j; 0 marks an empty cell
    rows, cols = len(board), len(board[0])  # the board's number of rows and columns
    colours = range(1, max(v for row in board for v in row) + 1)  # the colours, 1 to the largest endpoint colour
    cells = [(i, j) for i in range(rows) for j in range(cols)]

    model = gp.Model("flow_free_game")

    # paint[i, j, c] is 1 when the cell in row i, column j has colour c; 0 otherwise.
    paint = model.addVars(rows, cols, colours, vtype=GRB.BINARY, name="paint")
    # Each cell has exactly one colour (paint.sum(i, j, "*") adds paint[i, j, c] over all colours c).
    model.addConstrs((paint.sum(i, j, "*") == 1 for i, j in cells), name="one_colour")
    # B[i][j] is the colour of the cell in row i, column j.
    B = [[gp.quicksum(c * paint[i, j, c] for c in colours) for j in range(cols)] for i in range(rows)]

    # Each pair of orthogonally adjacent cells is an edge.
    edges = [((i, j), (i + di, j + dj)) for i, j in cells for di, dj in ((0, 1), (1, 0))
             if i + di < rows and j + dj < cols]
    # same[e] is 1 when the two cells of edge e share a colour: it is forced to 1 when both have
    # colour c, and to 0 when one has colour c and the other does not.
    same = model.addVars(range(len(edges)), vtype=GRB.BINARY, name="same")
    model.addConstrs((same[e] >= paint[u + (c,)] + paint[v + (c,)] - 1
                      for e, (u, v) in enumerate(edges) for c in colours), name="same_lo")
    model.addConstrs((same[e] <= 1 - paint[u + (c,)] + paint[v + (c,)]
                      for e, (u, v) in enumerate(edges) for c in colours), name="same_hi")
    # shares[u, v] is the same[e] of the edge between cells u and v, in either order.
    shares = {}
    for e, (u, v) in enumerate(edges):
        shares[u, v] = shares[v, u] = same[e]

    def same_neighbours(i, j):
        """The number of orthogonal neighbours of cell (i, j) that share its colour."""
        return gp.quicksum(shares[(i, j), (k, l)] for k, l in
                           ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                           if 0 <= k < rows and 0 <= l < cols)

    # An endpoint keeps its colour and continues into exactly one neighbour of the same colour.
    model.addConstrs((paint[i, j, board[i][j]] == 1 for i, j in cells if board[i][j] != 0), name="endpoint")
    model.addConstrs((same_neighbours(i, j) == 1 for i, j in cells if board[i][j] != 0), name="pipe_end")
    # An empty cell lies on a pipe in the middle: exactly two neighbours share its colour.
    model.addConstrs((same_neighbours(i, j) == 2 for i, j in cells if board[i][j] == 0), name="pipe_middle")

    # Not enforced: that each colour forms a single pipe. A detached closed loop of a colour also
    # meets the degree rules above; the statement asks for a pipe joining each pair.

    # No objective: any colouring that meets the constraints solves the puzzle.

    # The board as a list of lists of colours, B[i][j] for the cell in row i, column j.
    return model, {"B": B}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
