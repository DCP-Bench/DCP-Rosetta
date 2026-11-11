# session3_exodus: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python session3_exodus.py

import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data. The statement gives the five ages, and the five
# children, countries and stories, named here in the order the output lists use.
AGES = [3, 5, 7, 8, 10]  # the five ages, in years
CATEGORIES = {
    "ages": ["age3", "age5", "age7", "age8", "age10"],
    "children": ["bernice", "carl", "debby", "sammy", "ted"],
    "countries": ["ethiopia", "kazakhstan", "lithuania", "morocco", "yemen"],
    "stories": ["burning_bush", "captivity", "moses_youth", "passover", "ten_commandments"],
}
# The five slots 1 to 5: each slot is one child, and the output reports the slot of each item.
SLOTS = range(1, 6)
# The largest age difference is 10 - 3 = 7 and the largest gap in a clue is 3, so 10
# relaxes a clue whose two children are not the ones it names.
BIG_M = 10


def create_model(instance):
    """Five children each have a different age, a family from a different country and a different part of the Exodus story. Match them so that the five clues hold."""
    model = gp.Model("session3_exodus")

    # at[item, s] is 1 when the item (an age, a child, a country or a story) belongs to the child on slot s.
    at = {(item, s): model.addVar(vtype=GRB.BINARY, name=f"at[{item},{s}]")
          for items in CATEGORIES.values() for item in items for s in SLOTS}
    # Each item is on exactly one slot.
    for items in CATEGORIES.values():
        model.addConstrs((gp.quicksum(at[item, s] for s in SLOTS) == 1 for item in items), name="placed")
        # Each slot has exactly one item of each category.
        model.addConstrs((gp.quicksum(at[item, s] for item in items) == 1 for s in SLOTS), name="one_per_slot")

    # age[s] is the age of the child on slot s.
    age = {s: gp.quicksum(AGES[k] * at[item, s] for k, item in enumerate(CATEGORIES["ages"])) for s in SLOTS}

    def older_by(older, younger, gap, name):
        """Clue: the child `older` is `gap` years older than the child `younger`."""
        # If `older` is on slot s1 and `younger` on slot s2, then age(s1) - age(s2) == gap.
        # Otherwise the constraint is relaxed by BIG_M.
        model.addConstrs((age[s1] - age[s2] - gap <= BIG_M * (2 - at[older, s1] - at[younger, s2])
                          for s1 in SLOTS for s2 in SLOTS), name=f"{name}_upper")
        model.addConstrs((age[s1] - age[s2] - gap >= -BIG_M * (2 - at[older, s1] - at[younger, s2])
                          for s1 in SLOTS for s2 in SLOTS), name=f"{name}_lower")

    # 1. Debby's family is from Lithuania: the two items are on the same slot.
    model.addConstrs((at["debby", s] == at["lithuania", s] for s in SLOTS), name="clue1")

    # 2. The child who told the Passover story is two years older than Bernice.
    older_by("passover", "bernice", 2, "clue2")

    # 3. The child from the Yemeni family is younger than the child from the Ethiopian family.
    model.addConstrs((age[s1] <= age[s2] - 1 + BIG_M * (2 - at["yemen", s1] - at["ethiopia", s2])
                      for s1 in SLOTS for s2 in SLOTS), name="clue3")

    # 4. The child from the Moroccan family is three years older than Ted.
    older_by("morocco", "ted", 3, "clue4")

    # 5. Sammy is three years older than the child who told of Moses's youth.
    older_by("sammy", "moses_youth", 3, "clue5")

    # Each category's items as the slot numbers (1 to 5) they sit on, in the statement's order.
    outputs = {name: [gp.quicksum(s * at[item, s] for s in SLOTS) for item in items]
               for name, items in CATEGORIES.items()}
    return model, outputs


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
