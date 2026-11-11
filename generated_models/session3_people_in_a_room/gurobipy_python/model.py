# session3_people_in_a_room: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python session3_people_in_a_room.py

import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data; these numbers are from the problem statement.
TOTAL_PEOPLE = 13  # the number of people
NUM_MALES = 4  # how many of them are male
RATIO_FEMALES, RATIO_MALES = 7, 3  # the most females per male in the room is 7/3


def create_model(instance):
    """Order 13 people entering a room, 4 of them male, so that the ratio of females to males in the room at any one time is no greater than 7/3."""
    model = gp.Model("session3_people_in_a_room")

    # sequence[i] is 1 when the (i+1)-th person to enter is female and 0 when male.
    sequence = [model.addVar(vtype=GRB.BINARY, name=f"female[{i}]") for i in range(TOTAL_PEOPLE)]

    # Exactly 4 of the 13 people are male, so 9 are female.
    model.addConstr(gp.quicksum(sequence) == TOTAL_PEOPLE - NUM_MALES, name="number_of_males")

    # After each of the first i people has entered, for i = 1 to 12, the females and males in the
    # room satisfy females / males <= 7 / 3, written without division as 3 * females <= 7 * males.
    # So a room with no males has no females. The full room of 13 (9 females, 4 males) has
    # 9/4 < 7/3, so it needs no check.
    model.addConstrs((RATIO_MALES * gp.quicksum(sequence[:i]) <= RATIO_FEMALES * (i - gp.quicksum(sequence[:i]))
                      for i in range(1, TOTAL_PEOPLE)), name="ratio")

    return model, {"sequence": sequence}


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
