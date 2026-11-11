# appointment_scheduling: a Gurobi (Python) model from DCP Rosetta.
# Download the `appointment_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python appointment_scheduling.py appointment_scheduling.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Schedule each person into one interview slot in which they are free, with no two people in the same slot."""
    free = instance["m"]  # free[i][j] is 1 when person i is free in slot j, and 0 when busy
    n = len(free)  # the number of people, which is also the number of slots
    people = range(n)

    model = gp.Model("appointment_scheduling")

    # x[i, j] is 1 when person i is interviewed in slot j, and 0 when not
    x = model.addVars(people, people, vtype=GRB.BINARY, name="x")

    # Each person is interviewed in exactly one slot.
    model.addConstrs((x.sum(i, "*") == 1 for i in people), name="person")

    # That slot must be one where the person is free: the sum counts x[i, j] weighted by free[i][j],
    # so it is 1 only when the one slot taken is a free one.
    model.addConstrs((gp.quicksum(free[i][j] * x[i, j] for j in people) == 1 for i in people),
                     name="free")

    # Each slot is given to exactly one person.
    model.addConstrs((x.sum("*", j) == 1 for j in people), name="slot")

    # No objective: any assignment that meets these constraints is a solution.
    return model, {"x": [[x[i, j] for j in people] for i in people]}


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
