# allergy: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python allergy.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Match four friends (Debra, Janet, Hugh and Rick) to a surname and to an allergy each,
    from the clues given."""
    # The puzzle has no instance data: the friends, foods, surnames and clues are fixed by the statement.
    n = 4  # four friends, four foods and four surnames
    friends = range(n)  # Debra = 0, Janet = 1, Hugh = 2, Rick = 3
    debra, janet, hugh, rick = friends
    foods = ["eggs", "mold", "nuts", "ragweed"]
    surnames = ["baxter", "lemon", "malone", "fleet"]

    model = gp.Model("allergy")

    # has_food[f, p] is 1 when friend p is allergic to food f
    has_food = model.addVars(n, n, vtype=GRB.BINARY, name="has_food")
    # has_name[s, p] is 1 when friend p has surname s
    has_name = model.addVars(n, n, vtype=GRB.BINARY, name="has_name")

    # Each food and each surname belongs to exactly one friend
    # (has_food.sum(f, "*") adds over the friends, has_name.sum(s, "*") likewise)
    model.addConstrs((has_food.sum(f, "*") == 1 for f in range(n)), name="food_one_friend")
    model.addConstrs((has_name.sum(s, "*") == 1 for s in range(n)), name="surname_one_friend")
    # Each friend has exactly one allergy and exactly one surname
    # (has_food.sum("*", p) adds over the foods, has_name.sum("*", p) over the surnames)
    model.addConstrs((has_food.sum("*", p) == 1 for p in friends), name="friend_one_food")
    model.addConstrs((has_name.sum("*", p) == 1 for p in friends), name="friend_one_surname")

    # The foods and surnames named in the clues, as positions in the lists above
    eggs, mold, ragweed = 0, 1, 3
    baxter, lemon, fleet = 0, 1, 3

    # Rick is not allergic to mold.
    model.addConstr(has_food[mold, rick] == 0)
    # Baxter is allergic to eggs: the friend surnamed Baxter is the friend allergic to eggs.
    model.addConstrs((has_name[baxter, p] == has_food[eggs, p] for p in friends), name="baxter_eggs")
    # Hugh is neither surnamed Lemon nor Fleet.
    model.addConstrs((has_name[s, hugh] == 0 for s in (lemon, fleet)), name="hugh_surname")
    # Debra is allergic to ragweed.
    model.addConstr(has_food[ragweed, debra] == 1)
    # Janet (who isn't Lemon) is neither allergic to eggs nor to mold.
    model.addConstr(has_name[lemon, janet] == 0)
    model.addConstr(has_food[eggs, janet] == 0)
    model.addConstr(has_food[mold, janet] == 0)

    # Each food and surname is reported as the friend it belongs to (Debra 0 .. Rick 3).
    # Each sum has exactly one friend with a 1, so the weighted sum is that friend's index.
    food = {f: gp.quicksum(p * has_food[i, p] for p in friends) for i, f in enumerate(foods)}
    name = {s: gp.quicksum(p * has_name[i, p] for p in friends) for i, s in enumerate(surnames)}
    return model, {**food, **name}


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
