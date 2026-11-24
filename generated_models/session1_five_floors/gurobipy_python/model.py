# session1_five_floors: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python session1_five_floors.py

import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: five people (PEOPLE, the first letters of their names)
# and five floors (FLOORS, 1 to 5, from the statement).
PEOPLE = "BCFMS"
FLOORS = range(1, 6)


def create_model(instance):
    """Five floors: Baker, Cooper, Fletcher, Miller and Smith each live on a different one of five floors; find which."""
    model = gp.Model("session1_five_floors")

    # on[p, f] is 1 when person p lives on floor f, and 0 when not.
    on = model.addVars(PEOPLE, FLOORS, vtype=GRB.BINARY, name="on")
    # Each person lives on exactly one floor.
    model.addConstrs((on.sum(p, "*") == 1 for p in PEOPLE), name="one_floor")
    # floor[p] is the floor person p lives on, read back from on.
    floor = {p: gp.quicksum(f * on[p, f] for f in FLOORS) for p in PEOPLE}

    # They all live on different floors: each floor has exactly one person.
    model.addConstrs((on.sum("*", f) == 1 for f in FLOORS), name="different")

    # Baker does not live on the fifth floor.
    model.addConstr(on["B", 5] == 0, name="baker")
    # Cooper does not live on the first floor.
    model.addConstr(on["C", 1] == 0, name="cooper")
    # Fletcher lives on neither the fifth nor the first floor.
    model.addConstr(on["F", 5] + on["F", 1] == 0, name="fletcher")
    # Miller lives on a higher floor than Cooper.
    model.addConstr(floor["M"] >= floor["C"] + 1, name="miller_above_cooper")

    # Smith is not on a floor next to Fletcher's, and Fletcher is not on a floor next to Cooper's:
    # for each pair, the two never sit on floors f and f + 1 (in either order). range(1, 5) gives f with f + 1 a floor.
    for a, b in (("S", "F"), ("F", "C")):
        model.addConstrs((on[a, f] + on[b, f + 1] <= 1 for f in range(1, 5)), name=f"not_adjacent[{a},{b}]")
        model.addConstrs((on[b, f] + on[a, f + 1] <= 1 for f in range(1, 5)), name=f"not_adjacent[{b},{a}]")

    # No objective: the puzzle only asks for floors that obey the rules.
    return model, {p: floor[p] for p in PEOPLE}


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
