# csplib_015_schurs_lemma: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_015_schurs_lemma.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_015_schurs_lemma.py csplib_015_schurs_lemma.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Schur's lemma: put the balls 1 to n into three boxes so that no three balls x, y and x + y = z all lie in the same box."""
    n = instance["n"]  # the balls are labelled 1 to n
    c = instance["c"]  # the number of boxes (three in the statement)
    balls = range(1, n + 1)
    boxes = range(1, c + 1)

    model = gp.Model("schurs_lemma")

    # inbox[i, j] is 1 when ball i is in box j.
    inbox = model.addVars(balls, boxes, vtype=GRB.BINARY, name="inbox")

    # Each ball is in exactly one box.
    model.addConstrs((inbox.sum(i, "*") == 1 for i in balls), name="one_box")

    # For every x + y = z with z at most n, the three balls are not all in the same box, so
    # their box counts sum to at most 2. When x == y, ball x is counted twice, which forbids
    # balls x and z sharing a box.
    model.addConstrs((inbox[x, j] + inbox[y, j] + inbox[x + y, j] <= 2
                      for x in balls for y in balls if x + y <= n for j in boxes), name="no_triple")

    # No objective: any assignment that meets the constraints is an answer.
    # Each ball's box is the box number j with inbox[i, j] = 1.
    return model, {"balls": [gp.quicksum(j * inbox[i, j] for j in boxes) for i in balls]}


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
