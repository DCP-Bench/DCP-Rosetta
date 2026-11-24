# zebra: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python zebra.py

import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data. The five houses, numbered 0 (leftmost) to 4 (rightmost).
HOUSES = range(5)
# The five colours, nations, jobs, pets and drinks, as the statement names them.
CATEGORIES = {
    "colors": ["yellow", "green", "red", "white", "blue"],
    "nations": ["italy", "spain", "japan", "england", "norway"],
    "jobs": ["painter", "sculptor", "diplomat", "pianist", "doctor"],
    "pets": ["cat", "zebra", "bear", "snails", "horse"],
    "drinks": ["milk", "water", "tea", "coffee", "juice"],
}


def create_model(instance):
    """Zebra puzzle: five houses in a row, each with one colour, nation, job, pet and drink,
    chosen so that the clues about who lives where hold. Find the house of every item."""
    model = gp.Model("zebra")

    # at[item, h] is 1 when the item (a colour, nation, job, pet or drink) is in house h.
    at = {}
    for items in CATEGORIES.values():
        for item in items:
            for h in HOUSES:
                at[item, h] = model.addVar(vtype=GRB.BINARY, name=f"at[{item},{h}]")
        # Each item of a category is in exactly one house.
        model.addConstrs((gp.quicksum(at[item, h] for h in HOUSES) == 1 for item in items),
                         name="placed")
        # Each house has exactly one item of each category (so the five items fill the five houses).
        model.addConstrs((gp.quicksum(at[item, h] for item in items) == 1 for h in HOUSES),
                         name="one_per_house")

    def house(item):
        """The house number of an item: the sum of h over the houses h it is in."""
        return gp.quicksum(h * at[item, h] for h in HOUSES)

    def same(x, y):
        """Items x and y are in the same house."""
        model.addConstrs((at[x, h] == at[y, h] for h in HOUSES), name=f"{x}_with_{y}")

    def next_to(x, y):
        """Item x is in a house next to the house of item y."""
        for h in HOUSES:
            beside = [at[y, k] for k in (h - 1, h + 1) if k in HOUSES]
            model.addConstr(at[x, h] <= gp.quicksum(beside), name=f"{x}_next_to_{y}[{h}]")

    same("painter", "horse")            # the painter owns the horse
    same("diplomat", "coffee")          # the diplomat drinks coffee
    same("white", "milk")               # the one who drinks milk lives in the white house
    same("spain", "painter")            # the Spaniard is a painter
    same("england", "red")              # the Englishman lives in the red house
    same("snails", "sculptor")          # the snails are owned by the sculptor
    # the green house is immediately on the left of the red one
    model.addConstr(house("green") + 1 == house("red"), name="green_left_of_red")
    # the Norwegian lives immediately on the right of the blue house
    model.addConstr(house("blue") + 1 == house("norway"), name="norway_right_of_blue")
    same("doctor", "milk")              # the doctor drinks milk
    same("japan", "diplomat")           # the diplomat is Japanese
    same("norway", "zebra")             # the Norwegian owns the zebra
    next_to("green", "white")           # the green house is next to the white one
    next_to("horse", "diplomat")        # the horse is owned by the neighbour of the diplomat
    # the Italian lives in the red, white or green house
    model.addConstrs((at["italy", h] <= at["red", h] + at["white", h] + at["green", h]
                      for h in HOUSES), name="italy")

    # Each category's house numbers, as a list in the statement's order.
    return model, {name: [house(item) for item in items] for name, items in CATEGORIES.items()}


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
