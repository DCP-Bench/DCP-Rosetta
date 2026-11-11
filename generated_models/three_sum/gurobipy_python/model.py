# three_sum: a Gurobi (Python) model from DCP Rosetta.
# Download the `three_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python three_sum.py three_sum.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Zero sum: find some of the given integers that add up to zero, choosing exactly m of them."""
    nums = instance["nums"]  # nums[i]: the i-th integer
    m = instance["m"]        # how many integers to choose; the statement says only "a number of", so the instance fixes it
    items = range(len(nums))

    model = gp.Model("three_sum")

    # indices[i] is 1 when nums[i] is chosen, and 0 when not.
    indices = model.addVars(items, vtype=GRB.BINARY, name="indices")

    # The chosen integers add up to zero.
    model.addConstr(gp.quicksum(nums[i] * indices[i] for i in items) == 0, name="zero_sum")

    # Exactly m integers are chosen; m comes from the instance, not from the statement.
    model.addConstr(indices.sum() == m, name="count")

    # No objective: any choice that meets both constraints is an answer.
    return model, {"indices": [indices[i] for i in items]}


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
