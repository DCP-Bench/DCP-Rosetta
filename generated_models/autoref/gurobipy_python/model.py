# autoref: a Gurobi (Python) model from DCP Rosetta.
# Download the `autoref.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python autoref.py autoref.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Find a sequence s of n + 2 numbers in which each number i from 0 to n occurs exactly s[i] times, and whose last number s[n + 1] is m."""
    n = instance["n"]  # the series has n + 2 numbers, and the occurrences of each i from 0 to n are counted
    m = instance["m"]  # the required last number, s[n + 1]
    places = range(n + 2)  # positions 0 to n + 1 of the sequence
    # Not from the statement: every number is limited to 0..n. This rules out valid series such as
    # (4, 0, 0, 0, 0) for n = 3, m = 0, and makes every m > n infeasible.
    values = range(n + 1)

    model = gp.Model("autoref")

    # holds[p, v] is 1 when s[p] = v. One-hot values let the counts be read off linearly.
    holds = model.addVars(places, values, vtype=GRB.BINARY, name="holds")
    # Each position p holds exactly one number.
    model.addConstrs((holds.sum(p, "*") == 1 for p in places), name="one_value")
    # s[p] is the number at position p, as a linear expression.
    s = [gp.quicksum(v * holds[p, v] for v in values) for p in places]

    # For each i from 0 to n, the number of positions holding i is s[i].
    model.addConstrs((holds.sum("*", i) == s[i] for i in values), name="count")

    # The last position holds m.
    model.addConstr(s[n + 1] == m, name="last_is_m")

    # No objective: any sequence that meets the constraints solves the problem.

    return model, {"s": s}


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
