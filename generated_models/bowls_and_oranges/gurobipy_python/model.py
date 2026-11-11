# bowls_and_oranges: a Gurobi (Python) model from DCP Rosetta.
# Download the `bowls_and_oranges.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python bowls_and_oranges.py bowls_and_oranges.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Bowls and oranges: place all m oranges in bowls numbered 1 to n, at most one orange per bowl, so that no three oranges are evenly spaced."""
    n = instance["n"]  # the number of bowls, placed in a line 1 metre apart
    m = instance["m"]  # the number of oranges to place
    oranges = range(m)

    model = gp.Model("bowls_and_oranges")

    # x[i] is the bowl of the i-th orange, the oranges listed in ascending order of bowl.
    # Bowls are numbered 1 to n. The statement does not number them; numbering from 1 is the
    # convention of the printed list.
    x = model.addVars(oranges, lb=1, ub=n, vtype=GRB.INTEGER, name="x")
    # One orange per bowl, and the list ascending as the output requires: each orange
    # lies in a later bowl than the one before it.
    model.addConstrs((x[i] >= x[i - 1] + 1 for i in range(1, m)), name="ascending")

    # No three oranges A < B < C in list order are evenly spaced: the distance from A
    # to B is not the distance from B to C, i.e. 2*x[B] - x[A] - x[C] is not 0.
    # gurobipy has no "not equal", so the binary wider[a,b,c] picks the side: 1 when the
    # gap is at least 1 (A to B is the longer), 0 when it is at most -1. The gap is an
    # integer, so these two cases cover every value except 0.
    triples = [(a, b, c) for a in oranges for b in range(a + 1, m) for c in range(b + 1, m)]
    wider = model.addVars(triples, vtype=GRB.BINARY, name="wider")
    model.addConstrs(((wider[a, b, c] == 1) >> (2 * x[b] - x[a] - x[c] >= 1) for a, b, c in triples),
                     name="first_longer")
    model.addConstrs(((wider[a, b, c] == 0) >> (2 * x[b] - x[a] - x[c] <= -1) for a, b, c in triples),
                     name="second_longer")

    # No objective: any placement that meets the rules is a solution.
    # x: the bowls of the oranges, in ascending order.
    return model, {"x": [x[i] for i in oranges]}


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
