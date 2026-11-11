# clock_triplets: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python clock_triplets.py

import gurobipy as gp
from gurobipy import GRB

n = 12      # the numbers 1 to 12, one for each place on the clock (from the statement)
limit = 21  # no three adjacent numbers may sum to more than this (from the statement)


def create_model(instance):
    """Clock triplets: arrange 1..12 around a clock face so that no three adjacent numbers sum to more than 21."""
    places = range(n)
    numbers = range(1, n + 1)

    model = gp.Model("clock_triplets")

    # is_[i, v] is 1 when place i of the clock shows the number v, and 0 when not
    is_ = model.addVars(places, numbers, vtype=GRB.BINARY, name="is")

    # Each place shows exactly one number.
    model.addConstrs((is_.sum(i, "*") == 1 for i in places), name="one_number")

    # Each number appears on exactly one place.
    model.addConstrs((is_.sum("*", v) == 1 for v in numbers), name="used_once")

    # x[i] is the number shown at place i.
    x = [gp.quicksum(v * is_[i, v] for v in numbers) for i in places]

    # Three adjacent places, going round the clock: i, i-1 and i-2. Python's x[-1] is the
    # last place, so the triplets wrap round the clock for the first two places.
    # No three adjacent numbers sum to more than the limit.
    model.addConstrs((x[i] + x[i - 1] + x[i - 2] <= limit for i in places), name="triplet")

    return model, {"x": x}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
