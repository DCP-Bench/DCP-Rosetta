# big_bang2: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python big_bang2.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Find five six-faced dice, each face valued from 1 to 12, so that the dice beat
    each other exactly as Rock, Paper, Scissors, Lizard and Spock beat each other."""
    # The puzzle has no instance data: the dice, faces, face values and the ten
    # 'beats' relations all come from the statement.
    rock, paper, scissors, lizard, spock = range(5)  # the five dice, in the statement's order
    m, n, f = 5, 6, 12  # m dice, n faces per die, face values from 1 to f (from the statement)

    # (w, l): die w beats die l; the ten 'beats' relations of the statement, in its order
    edge = [
        (rock, scissors), (rock, lizard),
        (paper, rock), (paper, spock),
        (scissors, paper), (scissors, lizard),
        (lizard, paper), (lizard, spock),
        (spock, rock), (spock, scissors),
    ]
    faces = range(n)

    model = gp.Model("big_bang2")

    # dice[i, j] is the value of face j of die i, an integer from 1 to 12; values may repeat
    dice = model.addVars(m, n, lb=1, ub=f, vtype=GRB.INTEGER, name="dice")

    # For each beats relation (w, l), higher[x, y] is 1 only when face x of die w is
    # strictly larger than face y of die l. The beats relation is then: die w beats die l
    # when its face is strictly larger in more than half of the n * n face pairs.
    for (w, l) in edge:
        higher = model.addVars(faces, faces, vtype=GRB.BINARY, name=f"higher[{w},{l}]")
        model.addConstrs(((higher[x, y] == 1) >> (dice[w, x] >= dice[l, y] + 1)
                          for x in faces for y in faces), name=f"face_pair[{w},{l}]")
        # More than half of the 36 face pairs, so at least 19 of them (the statement's 'more than half').
        model.addConstr(higher.sum() >= (n * n) // 2 + 1, name=f"beats[{w},{l}]")

    # No objective: any dice that meet the constraints solve the puzzle.

    # The dice as five lists of six faces, in the order Rock, Paper, Scissors, Lizard, Spock.
    return model, {"dice": [[dice[i, j] for j in faces] for i in range(m)]}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
