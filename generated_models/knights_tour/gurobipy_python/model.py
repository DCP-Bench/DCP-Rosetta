# knights_tour: a Gurobi (Python) model from DCP Rosetta.
# Download the `knights_tour.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python knights_tour.py knights_tour.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Knight's tour: number the squares of an n-by-n board 0..n*n-1 in the order a knight visits them, every square once, each move a knight's move."""
    n = instance["n"]  # the board has n rows and n columns
    N = n * n          # the number of squares, which is also the number of moves plus one
    squares = [(i, j) for i in range(n) for j in range(n)]
    # the eight jumps of a knight, as (row change, column change)
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

    model = gp.Model("knights_tour")

    # x[i, j] is the move number at which the knight is on square (i, j), from 0 to n*n-1 as the statement says.
    x = {s: model.addVar(lb=0, ub=N - 1, vtype=GRB.INTEGER, name=f"x[{s[0]},{s[1]}]") for s in squares}

    # move[p, q] is 1 when the knight's move from square p is to square q, and 0 when not.
    # It exists only for squares a knight's move apart. A one-hot of every move number on every
    # square would need (n*n)**2 binaries, beyond the licence's 2000-variable limit at n = 10.
    move = {}
    for (i, j) in squares:
        for a, b in knight_moves:
            if 0 <= i + a < n and 0 <= j + b < n:
                move[(i, j), (i + a, j + b)] = model.addVar(vtype=GRB.BINARY, name=f"move[{i},{j},{i + a},{j + b}]")

    # When the knight moves from p to q, the number on q is one more than the number on p.
    for (p, q), m in move.items():
        model.addConstr((m == 1) >> (x[q] == x[p] + 1), name=f"next_number[{p},{q}]")

    # The knight leaves each square at most once (the moves out of p add up to at most 1).
    model.addConstrs((gp.quicksum(m for (s, _), m in move.items() if s == p) <= 1 for p in squares), name="leave")
    # The knight enters each square at most once (the moves into p add up to at most 1).
    model.addConstrs((gp.quicksum(m for (_, t), m in move.items() if t == p) <= 1 for p in squares), name="enter")
    # The moves form one path through all n*n squares, which has n*n - 1 moves. The numbers grow
    # along the path, so there are no loops, and the squares get the numbers 0..n*n-1, each once.
    model.addConstr(gp.quicksum(move.values()) == N - 1, name="tour_length")

    # x[i][j] is the move number of square (i, j)
    return model, {"x": [[x[i, j] for j in range(n)] for i in range(n)]}


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
