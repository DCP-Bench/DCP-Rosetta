# circular_table_averbach_1_2: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python circular_table_averbach_1_2.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Three card players X, Y and Z, of different nationalities (American, English, French), sit round a table and each passes three cards to the person on their right. Find where each player and each nationality sits, from the clues about who passed cards to whom."""
    # The puzzle has no instance data. Seats are numbered 0, 1, 2 so that 1 is right of 0, 2 right
    # of 1 and 0 right of 2 (the statement's convention).
    n = 3  # the number of seats, from the statement
    seats = range(n)
    people = ["x", "y", "z", "american", "english", "french"]

    model = gp.Model("circular_table")

    # at[p, s] is 1 when player or nationality p sits on seat s.
    at = model.addVars(people, seats, vtype=GRB.BINARY, name="at")
    # Each player and each nationality sits on exactly one seat.
    model.addConstrs((at.sum(p, "*") == 1 for p in people), name="one_seat")

    # Each seat holds exactly one of the three players, and exactly one of the three nationalities.
    model.addConstrs((gp.quicksum(at[p, s] for p in people[:3]) == 1 for s in seats), name="one_player_per_seat")
    model.addConstrs((gp.quicksum(at[p, s] for p in people[3:]) == 1 for s in seats), name="one_nationality_per_seat")

    # Y passed three hearts to the American, who is on Y's right: when Y is on seat s,
    # the American is on seat s + 1 (counting round the table).
    model.addConstrs((at["american", (s + 1) % n] == at["y", s] for s in seats), name="american_right_of_y")

    # X passed cards to the person who passed theirs to the Frenchwoman. Cards go to the right, so
    # X is on the Frenchwoman's right: when she is on seat s, X is on seat s + 1.
    model.addConstrs((at["x", (s + 1) % n] == at["french", s] for s in seats), name="x_right_of_french")

    # The output for each player or nationality is the seat it sits on (0, 1 or 2);
    # equal numbers mean the same player and nationality.
    return model, {p: gp.quicksum(s * at[p, s] for s in seats) for p in people}


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
