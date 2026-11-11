# four_islands: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python four_islands.py

import gurobipy as gp
from gurobipy import GRB


# The problem has no instance data: all of it comes from the statement. The islands sit on a map
# A B
# C D
# with A north-west, B north-east, C south-west and D south-east. Bridges join A-B and C-D (east-west)
# and A-C and B-D (north-south). The map positions are numbered A=0, B=1, C=2, D=3.
A, B, C, D = range(4)
POSITIONS = range(4)
ISLANDS = ["Pwana", "Quero", "Rayou", "Skern"]  # the four islands
EXPORTS = ["alabaster", "bananas", "coconuts", "durian_fruit"]  # the four primary exports
ATTRACTIONS = ["resort_hotel", "ice_skating_rink", "jai_alai_stadium", "koala_preserve"]  # the four tourist attractions


def create_model(instance):
    """Four islands: find the name, primary export and tourist attraction of each of four islands
    on a map, from the clues about where each one lies."""
    model = gp.Model("four_islands")

    # at[item, p] is 1 when that island, export or attraction is at map position p, and 0 when not.
    at = model.addVars(ISLANDS + EXPORTS + ATTRACTIONS, POSITIONS, vtype=GRB.BINARY, name="at")

    for group in (ISLANDS, EXPORTS, ATTRACTIONS):
        # Each item of the group is at exactly one map position (at.sum(item, "*") adds over the positions).
        model.addConstrs((at.sum(item, "*") == 1 for item in group), name="placed")
        # Each map position holds exactly one item of the group.
        model.addConstrs((gp.quicksum(at[item, p] for item in group) == 1 for p in POSITIONS),
                         name="one_per_position")

    def one_of(name, pairs):
        """At least one of the listed options holds. Each option says that one item is at one position
        and another item at another position; its binary is 1 only if both placements hold."""
        options = []
        for k, ((x, px), (y, py)) in enumerate(pairs):
            w = model.addVar(vtype=GRB.BINARY, name=f"{name}[{k}]")
            model.addConstr(w <= at[x, px])
            model.addConstr(w <= at[y, py])
            options.append(w)
        model.addConstr(gp.quicksum(options) >= 1, name=name)

    # 1. The island with the koala preserve is due south of Pwana.
    one_of("clue1", [(("Pwana", A), ("koala_preserve", C)), (("Pwana", B), ("koala_preserve", D))])

    # 2. The island with the alabaster quarry is due west of Quero.
    one_of("clue2", [(("alabaster", A), ("Quero", B)), (("alabaster", C), ("Quero", D))])

    # 3. The island with the resort hotel is due east of the one that exports durian fruit.
    one_of("clue3", [(("durian_fruit", A), ("resort_hotel", B)), (("durian_fruit", C), ("resort_hotel", D))])

    # 4. Skern and the island with the jai alai stadium are joined by a north-south bridge.
    one_of("clue4", [(("Skern", A), ("jai_alai_stadium", C)), (("Skern", C), ("jai_alai_stadium", A)),
                     (("Skern", B), ("jai_alai_stadium", D)), (("Skern", D), ("jai_alai_stadium", B))])

    # 5. Rayou and the island that exports bananas are joined by an east-west bridge.
    one_of("clue5", [(("Rayou", A), ("bananas", B)), (("Rayou", B), ("bananas", A)),
                     (("Rayou", C), ("bananas", D)), (("Rayou", D), ("bananas", C))])

    # 6. The ice skating rink and the jai alai stadium are not joined by a bridge, so they are on
    # diagonally opposite corners (A and D, or B and C).
    one_of("clue6", [(("ice_skating_rink", A), ("jai_alai_stadium", D)),
                     (("ice_skating_rink", D), ("jai_alai_stadium", A)),
                     (("ice_skating_rink", B), ("jai_alai_stadium", C)),
                     (("ice_skating_rink", C), ("jai_alai_stadium", B))])

    # There is no objective: the clues determine the answer.

    # position(item) is the map position of an item, as a number (the item is at exactly one position).
    def position(item):
        return gp.quicksum(p * at[item, p] for p in POSITIONS)

    return model, {
        "island": [position(i) for i in ISLANDS],
        "export": [position(e) for e in EXPORTS],
        "attraction": [position(t) for t in ATTRACTIONS],
    }


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
