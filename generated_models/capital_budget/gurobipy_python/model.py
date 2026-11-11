# capital_budget: a Gurobi (Python) model from DCP Rosetta.
# Download the `capital_budget.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python capital_budget.py capital_budget.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """A company chooses which investments to make, to obtain as much total net present value as possible without the cash outflows of the chosen investments exceeding the budget."""
    npv = instance["npv"]              # npv[i]: the net present value of investment i
    cash_flow = instance["cash_flow"]  # cash_flow[i]: the cash outflow that investment i requires now
    budget = instance["budget"]        # the total cash available for investment
    investments = range(len(npv))      # the investments, numbered from 0

    model = gp.Model("capital_budget")

    # x[i] is 1 when investment i is chosen, and 0 when not.
    x = model.addVars(investments, vtype=GRB.BINARY, name="x")

    # The cash outflows of the chosen investments stay within the budget.
    model.addConstr(gp.quicksum(cash_flow[i] * x[i] for i in investments) <= budget, name="budget")

    # z is the total net present value of the chosen investments, and it is maximised.
    z = gp.quicksum(npv[i] * x[i] for i in investments)
    model.setObjective(z, GRB.MAXIMIZE)

    return model, {"x": [x[i] for i in investments], "z": z}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.Params.MIPGap = 0  # prove the optimum; the default stops within 0.01% of it
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a proven optimum
        print("Objective value:", round(model.ObjVal))
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
