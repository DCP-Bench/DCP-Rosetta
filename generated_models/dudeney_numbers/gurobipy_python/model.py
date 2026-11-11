# dudeney_numbers: a Gurobi (Python) model from DCP Rosetta.
# Download the `dudeney_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python dudeney_numbers.py dudeney_numbers.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Find a perfect cube larger than 1, with at most n digits, whose digit sum equals its cube root."""
    n = instance["n"]  # the most digits the number may have
    # The cube root r. The digit sum of a number of at most n digits is at most 9n, so the root is at
    # most 9n; this bound is chosen here to keep the root finite, not taken from the statement.
    roots = range(1, 9 * n + 1)

    model = gp.Model("dudeney_numbers")
    # A solver setting, not from the statement: the coefficients reach 10^(n-1) and (9n)^3, so a
    # binary off by the default integrality tolerance could move the number by more than 1.
    model.Params.IntFeasTol = 1e-9

    # digits[i] is the i-th decimal digit of the number, counting from the left (most significant
    # first), from 0 to 9.
    digits = model.addVars(n, lb=0, ub=9, vtype=GRB.INTEGER, name="digits")
    # number is the candidate, from 0 up to the largest n-digit number 10^n - 1.
    number = model.addVar(lb=0, ub=10 ** n - 1, vtype=GRB.INTEGER, name="number")

    # is_root[r] is 1 when the cube root of the number is r; this keeps number = root^3 linear.
    is_root = model.addVars(roots, vtype=GRB.BINARY, name="is_root")
    model.addConstr(is_root.sum() == 1, name="one_root")
    # The cube root of the number, as a linear expression.
    cube_root = gp.quicksum(r * is_root[r] for r in roots)

    # The number is a perfect cube: it is the cube of its cube root.
    model.addConstr(number == gp.quicksum(r ** 3 * is_root[r] for r in roots), name="cube")

    # The digit sum of the number equals its cube root.
    model.addConstr(cube_root == digits.sum(), name="digit_sum")

    # The digits are the decimal digits of the number: digit i is worth 10^(n-1-i).
    model.addConstr(number == gp.quicksum(digits[i] * 10 ** (n - i - 1) for i in range(n)), name="digits")

    # The number is larger than 1, as the statement asks.
    model.addConstr(number >= 2, name="above_one")

    return model, {"number": number}


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
