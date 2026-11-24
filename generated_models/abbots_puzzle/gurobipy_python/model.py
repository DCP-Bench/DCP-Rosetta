# abbots_puzzle: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python abbots_puzzle.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Abbot's puzzle: 100 bushels shared among 100 people, 3 per man, 2 per woman,
    half per child, with five times as many women as men. Find the men, women and children."""
    # The puzzle's own constants, fixed by its statement.
    people = 100   # the 100 people who share the corn
    bushels = 100  # the 100 bushels of corn

    model = gp.Model("abbots_puzzle")

    # men, women and children are the head counts of each group.
    men = model.addVar(lb=0, ub=people, vtype=GRB.INTEGER, name="men")
    women = model.addVar(lb=0, ub=people, vtype=GRB.INTEGER, name="women")
    children = model.addVar(lb=0, ub=people, vtype=GRB.INTEGER, name="children")

    # Everyone is a man, a woman or a child.
    model.addConstr(men + women + children == people, name="people")

    # The corn adds up to 100 bushels: 3 per man, 2 per woman and half per child.
    # Doubled, so every coefficient is a whole number (6, 4 and 1 against 2 * bushels).
    model.addConstr(6 * men + 4 * women + children == 2 * bushels, name="bushels")

    # There are five times as many women as men.
    model.addConstr(women == 5 * men, name="women_five_times_men")

    return model, {"men": men, "women": women, "children": children}


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
