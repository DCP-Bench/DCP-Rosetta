# fifty_puzzle: a Gurobi (Python) model from DCP Rosetta.
# Download the `fifty_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python fifty_puzzle.py fifty_puzzle.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Choose which dummies to knock over so that the numbers on them add up to exactly the
    target sum, neither more nor less."""
    values = instance["values"]  # values[i]: the number on dummy i
    target_sum = instance["target_sum"]  # the sum the knocked-over numbers must add up to exactly
    dummies_ = range(len(values))  # the dummies, numbered 0 to len(values) - 1

    model = gp.Model("fifty_puzzle")

    # dummies[i] is 1 when dummy i is knocked over, and 0 when not.
    dummies = model.addVars(dummies_, vtype=GRB.BINARY, name="dummies")

    # The numbers on the knocked-over dummies add up to the target sum, neither more nor less.
    model.addConstr(gp.quicksum(values[i] * dummies[i] for i in dummies_) == target_sum,
                    name="target")

    # No objective: any choice of dummies that meets the target is a solution.

    return model, {"dummies": [dummies[i] for i in dummies_]}


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
