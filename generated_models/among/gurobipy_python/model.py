# among: a Gurobi (Python) model from DCP Rosetta.
# Download the `among.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python among.py among.json

import gurobipy as gp
from gurobipy import GRB

# Every x[i] lies in 0..7, as the problem statement fixes.
VALUES = range(8)


def create_model(instance):
    """Among: choose n values in 0..7 such that exactly m of them are among the values of v."""
    n = instance["n"]  # the number of values x to choose
    m = instance["m"]  # how many of the chosen values must be among v
    v = instance["v"]  # the listed values
    positions = range(n)

    model = gp.Model("among")

    # takes[i, a] is 1 when x[i] equals a; each x[i] takes exactly one value.
    takes = model.addVars(positions, VALUES, vtype=GRB.BINARY, name="takes")
    # Each x[i] takes exactly one value.
    model.addConstrs((takes.sum(i, "*") == 1 for i in positions), name="one_value")

    # Exactly m of the x[i] take a value in v. As in the problem's definition,
    # the count runs over every (i, value of v) pair, so a value listed twice in v
    # counts twice; a value outside 0..7 can never be taken and counts nothing.
    model.addConstr(gp.quicksum(takes[i, a] for i in positions for a in v if a in VALUES) == m,
                    name="among")

    # x[i] is the value chosen for position i.
    x = [gp.quicksum(a * takes[i, a] for a in VALUES) for i in positions]
    return model, {"x": x}


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
