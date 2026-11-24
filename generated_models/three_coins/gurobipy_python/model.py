# three_coins: a Gurobi (Python) model from DCP Rosetta.
# Download the `three_coins.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python three_coins.py three_coins.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Three coins: flip exactly num_moves coins, one per move, so that at the end all the coins face the same way (all heads or all tails)."""
    num_moves = instance["num_moves"]  # the number of moves, exactly
    init = instance["init"]            # init[j]: 1 when coin j starts tails, 0 when it starts heads
    n = len(init)                      # the number of coins
    coins = range(n)
    moves = range(1, num_moves + 1)

    model = gp.Model("three_coins")

    # steps[m][j] is 1 when coin j shows tails after m moves (row 0 is the start, row num_moves the end).
    steps = [[model.addVar(vtype=GRB.BINARY, name=f"tails[{m},{j}]") for j in coins]
             for m in range(num_moves + 1)]

    # The coins start in the given faces.
    model.addConstrs((steps[0][j] == init[j] for j in coins), name="start")

    # flipped[m, j] is 1 when move m flips coin j, that is when coin j shows a different face after
    # the move from before it: the exclusive or of the two values, written as four inequalities.
    flipped = model.addVars(moves, coins, vtype=GRB.BINARY, name="flipped")
    model.addConstrs((flipped[m, j] >= steps[m - 1][j] - steps[m][j] for m in moves for j in coins), name="flip_a")
    model.addConstrs((flipped[m, j] >= steps[m][j] - steps[m - 1][j] for m in moves for j in coins), name="flip_b")
    model.addConstrs((flipped[m, j] <= steps[m - 1][j] + steps[m][j] for m in moves for j in coins), name="flip_c")
    model.addConstrs((flipped[m, j] <= 2 - steps[m - 1][j] - steps[m][j] for m in moves for j in coins), name="flip_d")

    # Each move flips exactly one coin.
    model.addConstrs((gp.quicksum(flipped[m, j] for j in coins) == 1 for m in moves), name="one_flip")

    # all_tails is 1 when the coins end all tails and 0 when they end all heads: the final row is
    # all equal exactly when its tails count is either 0 or n.
    all_tails = model.addVar(vtype=GRB.BINARY, name="all_tails")
    model.addConstr(gp.quicksum(steps[num_moves]) == n * all_tails, name="all_same")

    # steps is the face of each coin after each move, as True for tails.
    return model, {"steps": steps}


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
