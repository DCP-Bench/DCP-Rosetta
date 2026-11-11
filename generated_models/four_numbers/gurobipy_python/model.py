# four_numbers: a Gurobi (Python) model from DCP Rosetta.
# Download the `four_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_numbers.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python four_numbers.py four_numbers.json

import gurobipy as gp
from gurobipy import GRB

# The statement says the three numbers lie between 1 and 10, inclusive.
LOW, HIGH = 1, 10
# The statement asks for a list of three numbers.
PARTS = range(3)


def create_model(instance):
    """Four numbers: find three integers from 1 to 10 such that every given number is a sum of some of the three."""
    numbers = instance["numbers"]  # numbers[i]: the i-th given number
    targets = range(len(numbers))

    model = gp.Model("four_numbers")

    # x[j] is the j-th of the three numbers, from 1 to 10.
    x = model.addVars(PARTS, lb=LOW, ub=HIGH, vtype=GRB.INTEGER, name="x")

    # uses[i, j] is 1 when x[j] is one of the numbers summed to make numbers[i], and 0 when not.
    uses = model.addVars(targets, PARTS, vtype=GRB.BINARY, name="uses")

    # part[i, j] is uses[i, j] * x[j], which is not linear as a product of two variables. It is
    # written with inequalities: part is 0 when uses is 0, and equals x[j] when uses is 1, using the
    # bounds 1..10 of x for the big-M terms.
    part = model.addVars(targets, PARTS, lb=0, ub=HIGH, vtype=GRB.INTEGER, name="part")
    for i in targets:
        for j in PARTS:
            model.addConstr(part[i, j] <= HIGH * uses[i, j], name=f"off_high[{i},{j}]")
            model.addConstr(part[i, j] >= LOW * uses[i, j], name=f"off_low[{i},{j}]")
            model.addConstr(part[i, j] <= x[j] - LOW * (1 - uses[i, j]), name=f"on_high[{i},{j}]")
            model.addConstr(part[i, j] >= x[j] - HIGH * (1 - uses[i, j]), name=f"on_low[{i},{j}]")

    # Each given number is the sum of the parts chosen for it: part.sum(i, "*") adds part[i, j] over all j.
    model.addConstrs((part.sum(i, "*") == numbers[i] for i in targets), name="sum")

    # x is the list of the three numbers.
    return model, {"x": [x[j] for j in PARTS]}


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
