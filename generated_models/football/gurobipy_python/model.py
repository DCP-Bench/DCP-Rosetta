# football: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python football.py

import gurobipy as gp
from gurobipy import GRB


# The problem has no instance data; the prices (in GBP thousands), the budget and the squad
# rules are the ones in the statement.
BUDGET = 30000  # the chairman's limit, GBP 30 million, in GBP thousands
# PRICES[t][j] is the price, in GBP thousands, of player j+1 of type t, in the order of the
# statement (goalkeepers g1-g3, defenders d1-d8, midfielders m1-m10, strikers s1-s5).
PRICES = {
    "goalkeeper": [730, 1280, 3880],
    "defender": [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570],
    "midfielder": [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],
    "striker": [4460, 6470, 7780, 8390, 9500],
}
# How many of each type must be bought: (at least, at most). Goalkeepers: exactly 1.
# Defenders and strikers: 2 or more. Midfielders: 3 or more. No upper limit is in the statement.
COUNT = {"goalkeeper": (1, 1), "defender": (2, None), "midfielder": (3, None), "striker": (2, None)}
MIN_SQUAD = 11  # the squad has at least eleven players in total


def create_model(instance):
    """Football: buy a squad of players, within the GBP 30 million budget, that spends as much of the budget as possible."""
    model = gp.Model("football")

    # buy[t, j] is 1 when player j+1 of type t is bought (see PRICES).
    buy = model.addVars([(t, j) for t, prices in PRICES.items() for j in range(len(prices))],
                        vtype=GRB.BINARY, name="buy")

    # The squad: exactly one goalkeeper, at least two defenders, at least three midfielders
    # and at least two strikers.
    for t, (low, high) in COUNT.items():
        model.addConstr(buy.sum(t, "*") >= low, name=f"at_least[{t}]")
        if high is not None:
            model.addConstr(buy.sum(t, "*") <= high, name=f"at_most[{t}]")

    # At least eleven players in total.
    model.addConstr(buy.sum() >= MIN_SQUAD, name="squad_size")

    # z is the total price of the squad, in GBP thousands; it may not go over the budget.
    z = model.addVar(lb=0, ub=BUDGET, vtype=GRB.INTEGER, name="z")
    model.addConstr(z == gp.quicksum(PRICES[t][j] * buy[t, j] for t, j in buy), name="total_price")

    # Objective: spend as much of the budget as possible, i.e. make the total price as large as it can be without going over the budget.
    model.setObjective(z, GRB.MAXIMIZE)

    return model, {"z": z}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.Params.OutputFlag = 0  # no solver log
    model.Params.MIPGap = 0  # prove the optimum; the default stops within 0.01% of it
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a proven optimum
        print("Objective value:", round(model.ObjVal))
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
