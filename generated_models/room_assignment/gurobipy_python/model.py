# room_assignment: a Gurobi (Python) model from DCP Rosetta.
# Download the `room_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python room_assignment.py room_assignment.json

from datetime import date, timedelta

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Room assignment: give each request one room for its whole stay, so that no two requests that overlap in time share a room."""
    max_rooms = instance["max_rooms"]  # the number of rooms, numbered 0 to max_rooms - 1
    starts = [date.fromisoformat(s) for s in instance["start_data"]]  # starts[i]: the day request i starts
    ends = [date.fromisoformat(e) for e in instance["end_data"]]  # ends[i]: the day request i ends
    preassigned = instance["preassigned_room_data"]  # preassigned[i]: the room request i already has, or -1 for none
    requests = range(len(starts))
    rooms = range(max_rooms)

    model = gp.Model("room_assignment")

    # in_room[i, r] is 1 when request i is assigned room r.
    in_room = model.addVars(requests, rooms, vtype=GRB.BINARY, name="in_room")
    # room_of[i] is the room of request i, the number r whose in_room[i, r] is 1.
    room_of = [gp.quicksum(r * in_room[i, r] for r in rooms) for i in requests]

    # Each request is given exactly one room, the same one for its whole stay.
    model.addConstrs((in_room.sum(i, "*") == 1 for i in requests), name="one_room")

    # A request that is already pre-assigned to a room gets that room.
    model.addConstrs((room_of[i] == preassigned[i] for i in requests if preassigned[i] != -1), name="preassigned")

    # A room serves one request at a time. Each day, the requests staying that day share out the rooms, at most one per room. A request stays from its start day up to, but not including, its end day (this convention is not in the statement; it is the reference's).
    day = min(starts)
    while day <= max(ends):
        present = [i for i in requests if starts[i] <= day < ends[i]]
        if len(present) > 1:
            model.addConstrs((gp.quicksum(in_room[i, r] for i in present) <= 1 for r in rooms), name=f"one_per_room[{day}]")
        day += timedelta(days=1)

    return model, {"room_assignments": room_of}


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
