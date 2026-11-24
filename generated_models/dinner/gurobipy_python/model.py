# dinner: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python dinner.py

import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data; the ranges, prices and totals below are
# the ones the puzzle states.


def create_model(instance):
    """Choose how many grandparents, parents and children go to dinner so that 20 people eat and the bill comes to exactly $20."""
    model = gp.Model("dinner")

    # grandparents: how many grandparents go to dinner, from 1 to 6
    grandparents = model.addVar(lb=1, ub=6, vtype=GRB.INTEGER, name="grandparents")
    # parents: how many parents go to dinner, from 1 to 10
    parents = model.addVar(lb=1, ub=10, vtype=GRB.INTEGER, name="parents")
    # children: how many children go to dinner, from 1 to 40
    children = model.addVar(lb=1, ub=40, vtype=GRB.INTEGER, name="children")

    # The bill is $20: grandparents cost $3, parents $2 and children $0.50.
    # Counted in half dollars to keep the coefficients integer: 40 half dollars.
    model.addConstr(6 * grandparents + 4 * parents + 1 * children == 20 * 2, name="cost")

    # There must be 20 people at dinner.
    model.addConstr(grandparents + parents + children == 20, name="people")

    return model, {"grandparents": grandparents, "parents": parents, "children": children}


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
