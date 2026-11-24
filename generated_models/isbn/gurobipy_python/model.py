# isbn: a Gurobi (Python) model from DCP Rosetta.
# Download the `isbn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python isbn.py isbn.json

import gurobipy as gp
from gurobipy import GRB

# An ISBN-13 has 13 digits (from the statement)
LENGTH = 13
# Weights of the first 12 digits, alternately 1 and 3 starting with 1 (from the statement);
# the check digit has weight 1
WEIGHTS = [1, 3] * 6


def create_model(instance):
    """Fill in the unknown digits of an ISBN-13 so that it starts with 978 or 979 and its check digit is valid."""
    known = instance["isbn_init"]  # known[i] is digit i of the given ISBN, or -1 where it is unknown

    model = gp.Model("isbn")

    # isbn[i] is digit i of the ISBN, counting from 0; each digit is between 0 and 9
    isbn = model.addVars(LENGTH, lb=0, ub=9, vtype=GRB.INTEGER, name="isbn")

    # Each known digit keeps its given value
    model.addConstrs((isbn[i] == known[i] for i in range(LENGTH) if known[i] != -1), name="known")

    # The number starts with 978 or 979: digit 0 is 9, digit 1 is 7, and digit 2 is 8 or 9
    model.addConstr(isbn[0] == 9, name="prefix0")
    model.addConstr(isbn[1] == 7, name="prefix1")
    model.addConstr(isbn[2] >= 8, name="prefix2")

    # Check digit: the weighted sum of the 13 digits is a multiple of 10. For a single check
    # digit this is the same as the statement's rule, check = (10 - sum % 10) % 10.
    # tens is that weighted sum divided by 10 (not from the statement: its upper bound comes
    # from the largest possible sum, all digits 9, and keeps it finite).
    tens = model.addVar(lb=0, ub=(9 * sum(WEIGHTS) + 9) // 10, vtype=GRB.INTEGER, name="tens")
    model.addConstr(gp.quicksum(w * isbn[i] for i, w in enumerate(WEIGHTS)) + isbn[LENGTH - 1]
                    == 10 * tens, name="check_digit")

    # The complete ISBN, as a list of its 13 digits
    return model, {"isbn": [isbn[i] for i in range(LENGTH)]}


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
