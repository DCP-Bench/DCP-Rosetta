# session1_thick_as_thieves: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python session1_thick_as_thieves.py

import gurobipy as gp
from gurobipy import GRB

# The six suspects (from the statement)
SUSPECTS = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]
# The getaway car was barely big enough to hold two (from the statement)
CAR_SEATS = 2


def create_model(instance):
    """Six suspects in a robbery: the innocent ones tell the truth and the guilty ones lie, and the
    getaway car held only two. Work out who is guilty."""
    model = gp.Model("session1_thick_as_thieves")

    # guilty[s] is 1 when suspect s is guilty
    guilty = {s: model.addVar(vtype=GRB.BINARY, name=s) for s in SUSPECTS}
    artie, bill, crackitt, dodgy, edgy, fingers = (guilty[s] for s in SUSPECTS)
    # total is the number of guilty suspects
    total = gp.quicksum(guilty.values())

    # The car held two, so at most two are guilty
    model.addConstr(total <= CAR_SEATS, name="car")

    # A suspect is guilty exactly when his statement is false.

    # Artie: "It wasn't me." This is false exactly when Artie is guilty, so the rule holds for
    # either value of artie and adds no constraint.

    # Bill: "Crackitt was in it up to his neck." Bill is guilty exactly when Crackitt is not.
    model.addConstr(bill == 1 - crackitt, name="bill_says")

    # Crackitt: "No I wasn't." As for Artie, the rule holds for either value and adds no constraint.

    # Dodgy: "If Crackitt did it, Bill did it with him." This is false exactly when Crackitt did it
    # and Bill did not, so dodgy = crackitt and not bill.
    model.addConstr(dodgy <= crackitt, name="dodgy_says_1")
    model.addConstr(dodgy <= 1 - bill, name="dodgy_says_2")
    model.addConstr(dodgy >= crackitt - bill, name="dodgy_says_3")

    # Edgy: "Nobody did it alone", that is, more than one is guilty. Edgy is guilty exactly when
    # that is false, that is, when at most one is guilty.
    model.addConstr((edgy == 1) >> (total <= 1), name="edgy_lies")
    model.addConstr((edgy == 0) >> (total >= 2), name="edgy_true")

    # Fingers: "It was Artie and Dodgy together." Fingers is guilty exactly when that is false.
    # both is 1 when Artie and Dodgy are both guilty (an auxiliary variable for this statement)
    both = model.addVar(vtype=GRB.BINARY, name="artie_and_dodgy")
    model.addConstr(both == gp.and_(artie, dodgy), name="both")
    model.addConstr(fingers == 1 - both, name="fingers_says")

    return model, dict(guilty)


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
