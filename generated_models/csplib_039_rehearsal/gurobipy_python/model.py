# csplib_039_rehearsal: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_039_rehearsal.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_039_rehearsal.py csplib_039_rehearsal.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """A concert has pieces of music of different durations, each played by its own set of
    players. Players arrive just before their first piece and leave just after their last;
    find the rehearsal order of the pieces that minimises the time players spend present
    but not playing."""
    n = instance["num_pieces"]  # the number of pieces, which is also the number of rehearsal slots
    num_players = instance["num_players"]  # the number of players in the orchestra
    duration = instance["duration"]  # duration[p] is the length of piece p
    plays = instance["rehearsal"]  # plays[pl][p] is 1 when player pl plays in piece p
    slots = range(n)
    pieces = range(n)
    players = range(num_players)

    model = gp.Model("csplib_039_rehearsal")

    # at[i, p] is 1 when piece p is rehearsed in slot i.
    at = model.addVars(slots, pieces, vtype=GRB.BINARY, name="at")
    # Each slot holds exactly one piece, and each piece is rehearsed in exactly one slot.
    model.addConstrs((at.sum(i, "*") == 1 for i in slots), name="slot")
    model.addConstrs((at.sum("*", p) == 1 for p in pieces), name="piece")

    # arrived[pl, i] is 1 in the slot where player pl arrives and every later slot; staying[pl, i]
    # is 1 in every slot up to and including the one where pl departs. The player is present in
    # slot i when both hold, which makes presence one contiguous block of slots.
    arrived = model.addVars(players, slots, vtype=GRB.BINARY, name="arrived")
    staying = model.addVars(players, slots, vtype=GRB.BINARY, name="staying")
    # Once arrived, a player stays arrived; once departed, a player never comes back.
    model.addConstrs((arrived[pl, i] <= arrived[pl, i + 1] for pl in players for i in range(n - 1)), name="arrive_once")
    model.addConstrs((staying[pl, i] >= staying[pl, i + 1] for pl in players for i in range(n - 1)), name="depart_once")
    # A player cannot depart before arriving: in every slot arrived or staying holds, so
    # arrived + staying - 1 is 0 or 1 and presence is never split.
    model.addConstrs((arrived[pl, i] + staying[pl, i] >= 1 for pl in players for i in slots), name="arrive_before_depart")
    # present[pl, i] is 1 exactly when both arrived[pl, i] and staying[pl, i] hold.
    present = {(pl, i): arrived[pl, i] + staying[pl, i] - 1 for pl in players for i in slots}

    # A player must be present in every slot where a piece they play is rehearsed. The statement
    # has players arrive just before their first piece and leave just after their last; here they
    # may stay longer, which only adds waiting, so the minimum never uses it.
    model.addConstrs(
        (gp.quicksum(at[i, p] for p in pieces if plays[pl][p]) <= present[pl, i] for pl in players for i in slots),
        name="present_to_play",
    )

    # waiting[pl, i, p] is 1 when player pl is present in slot i while piece p, which pl does not
    # play, is rehearsed there; the waiting time is duration[p] times this. It is binary, so the
    # objective is an exact integer; the constraint below forces it to 1 when it must be, and the
    # minimisation holds it at 0 otherwise.
    waiting = model.addVars(
        [(pl, i, p) for pl in players for i in slots for p in pieces if not plays[pl][p]],
        vtype=GRB.BINARY, name="waiting",
    )
    model.addConstrs(
        (waiting[pl, i, p] >= present[pl, i] + at[i, p] - 1 for (pl, i, p) in waiting),
        name="wait",
    )

    # Objective: the total waiting time; each slot in which a present player sits out a piece
    # adds that piece's duration.
    model.setObjective(gp.quicksum(duration[p] * waiting[pl, i, p] for (pl, i, p) in waiting), GRB.MINIMIZE)

    # rehearsal_order[i] is the piece rehearsed in slot i.
    rehearsal_order = [gp.quicksum(p * at[i, p] for p in pieces) for i in slots]
    return model, {"rehearsal_order": rehearsal_order}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
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
