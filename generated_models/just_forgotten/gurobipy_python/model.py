# just_forgotten: a Gurobi (Python) model from DCP Rosetta.
# Download the `just_forgotten.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python just_forgotten.py just_forgotten.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Joe's account number has each digit from 0 to n-1 exactly once, in some order. From the
    sets of digits he tried, and how many digits of each set were in their correct position,
    find the account number."""
    sets = instance["sets"]  # sets[k][i] is the digit in position i of the k-th number Joe tried
    correct = instance["num_correct_digits"]  # how many digits of each tried number are in their correct position
    n = len(sets[0])  # the number of digits in the account number
    positions = range(n)
    digits = range(n)

    model = gp.Model("just_forgotten")

    # digit_at[i, d] is 1 when position i of the account number holds digit d.
    digit_at = model.addVars(positions, digits, vtype=GRB.BINARY, name="digit_at")

    # Every position holds exactly one digit, and every digit 0 to n-1 is used exactly once.
    model.addConstrs((digit_at.sum(i, "*") == 1 for i in positions), name="position")
    model.addConstrs((digit_at.sum("*", d) == 1 for d in digits), name="digit")

    # In each tried number, exactly the given number of digits are in their correct position.
    for k, tried in enumerate(sets):
        model.addConstr(gp.quicksum(digit_at[i, tried[i]] for i in positions if tried[i] in digits)
                        == correct, name=f"set[{k}]")

    # x[i] is the digit in position i of the account number, as an expression over digit_at.
    x = [gp.quicksum(d * digit_at[i, d] for d in digits) for i in positions]
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
