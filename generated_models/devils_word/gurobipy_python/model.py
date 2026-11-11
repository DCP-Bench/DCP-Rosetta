# devils_word: a Gurobi (Python) model from DCP Rosetta.
# Download the `devils_word.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python devils_word.py devils_word.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Devil's word: put a plus or minus sign before each number of the array so that the signed numbers add up to the given total."""
    arr = instance["arr"]  # arr[i]: the i-th number of the array, which gets a sign
    total = instance["total"]  # the total the signed numbers must add up to (666 in the statement)
    n = len(arr)

    model = gp.Model("devils_word")

    # plus[i] is 1 when arr[i] gets a plus sign and 0 when it gets a minus sign, so each number gets exactly one sign.
    plus = [model.addVar(vtype=GRB.BINARY, name=f"plus[{i}]") for i in range(n)]

    # Each number with its sign: arr[i] when added, -arr[i] when subtracted.
    result = [arr[i] * (2 * plus[i] - 1) for i in range(n)]

    # The signed numbers add up to the total.
    model.addConstr(gp.quicksum(result) == total, name="total")

    # There is no objective: any signs that reach the total are a solution.
    return model, {"result": result}


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
