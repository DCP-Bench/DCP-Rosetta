# set_game: a Gurobi (Python) model from DCP Rosetta.
# Download the `set_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python set_game.py set_game.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Set game: find three different cards that form a set, where for each of the four features the
    three cards are either all the same or all different."""
    cards = instance["cards_data"]  # cards[c] is card c as [number, fill, colour, shape], each feature coded 1, 2 or 3
    n_cards = len(cards)
    slots = range(3)                # the three cards of the set, in slots 0, 1 and 2
    card_ids = range(n_cards)       # card c is the c-th card of the table

    model = gp.Model("set_game")

    # pick[k, c] is 1 when the card in slot k is card c, and 0 when not.
    pick = model.addVars(slots, card_ids, vtype=GRB.BINARY, name="pick")

    # Each slot holds exactly one card (pick.sum(k, "*") adds over the cards c).
    model.addConstrs((pick.sum(k, "*") == 1 for k in slots), name="one_card")

    # The three cards are different: each card is picked in at most one slot (pick.sum("*", c) adds over the slots k).
    model.addConstrs((pick.sum("*", c) <= 1 for c in card_ids), name="distinct")

    # For each feature f and each value v that the cards take in f: the number of the three chosen cards
    # showing v is 0, 1 or 3, never 2. This is exactly "all the same or all different" for the feature.
    # single[f, v] is 1 when exactly one chosen card shows v, and triple[f, v] is 1 when all three do.
    # The two cannot both be 1, and the count shown is single + 3 * triple.
    for f in range(len(cards[0])):
        for v in sorted({card[f] for card in cards}):
            shown = gp.quicksum(pick[k, c] for k in slots for c in card_ids if cards[c][f] == v)
            single = model.addVar(vtype=GRB.BINARY, name=f"single[{f},{v}]")
            triple = model.addVar(vtype=GRB.BINARY, name=f"triple[{f},{v}]")
            model.addConstr(single + triple <= 1, name=f"not_two[{f},{v}]")
            model.addConstr(shown == single + 3 * triple, name=f"all_or_none[{f},{v}]")

    # There is no objective: any three cards that meet the conditions are a solution.

    # winning_cards[k] is the index of the card in slot k: the sum of c * pick[k, c] over the cards c,
    # since exactly one of those terms is 1.
    return model, {"winning_cards": [gp.quicksum(c * pick[k, c] for c in card_ids) for k in slots]}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
