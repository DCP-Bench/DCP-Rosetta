# contracting_costs: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python contracting_costs.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Six tradesmen each charge a price for their work. A contractor paid a fixed total for
    each of six pairs of them, so find what each tradesman charges."""
    # The puzzle has no instance data: the six pairs and their totals are the statement's own.
    names = ["paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason"]  # the six tradesmen

    model = gp.Model("contracting_costs")

    # charge[p] is what tradesman p charges, in whole dollars. The lower bound 0 (a price is not
    # negative) is not in the statement; it cannot cut off the answer, because the six equations
    # below have the single solution 200, 900, 800, 300, 3000, 2300, all positive.
    charge = model.addVars(names, lb=0, vtype=GRB.INTEGER, name="charge")

    # The contractor's bill for each pair of tradesmen, in dollars, from the statement.
    pairs = [
        ("paper_hanger", "painter", 1100),
        ("painter", "plumber", 1700),
        ("plumber", "electrician", 1100),
        ("electrician", "carpenter", 3300),
        ("carpenter", "mason", 5300),
        ("mason", "painter", 3200),
    ]
    # Each pair of tradesmen together charges the amount the contractor paid for them.
    model.addConstrs(charge[p] + charge[q] == total for p, q, total in pairs)

    # No objective: any charges that meet the six totals answer the puzzle.
    return model, charge


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
