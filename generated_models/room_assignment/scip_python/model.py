# room_assignment: a SCIP (Python) model from DCP Rosetta.
# Download the `room_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python room_assignment.py room_assignment.json

from datetime import date

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Put each room request into one of the rooms so that a request keeps
    one room for its whole stay, and no room serves two requests at once.
    A request that already has a room keeps it."""
    max_rooms = instance["max_rooms"]  # the number of rooms; they are numbered 0 .. max_rooms - 1
    # Request i checks in on start_data[i] and out on end_data[i], both as YYYY-MM-DD dates.
    # The dates become day numbers, so that days can be counted.
    starts = [date.fromisoformat(s).toordinal() for s in instance["start_data"]]  # check-in day of each request
    ends = [date.fromisoformat(e).toordinal() for e in instance["end_data"]]  # check-out day of each request
    # preassigned_room_data[i] is the room request i must keep, or -1 when it has none
    preassigned = instance["preassigned_room_data"]
    n = len(starts)  # the number of requests

    model = Model("room_assignment")

    # x[i, r] is 1 when request i is put in room r, and 0 when not
    x = model.addMatrixVar((n, max_rooms), vtype="B", name="x")

    # Each request is in exactly one room for its whole stay.
    model.addMatrixCons(x.sum(axis=1) == 1)

    # A request with a pre-assigned room is fixed to that room.
    for i, room in enumerate(preassigned):
        if room >= 0:
            model.addCons(x[i, room] == 1)

    # A room serves at most one request on any day. A stay covers the days from its check-in day
    # up to, not including, its check-out day. The exclusive check-out is an assumption: the
    # statement does not say which day a stay ends, and this reading lets one request check out
    # on the day another checks in. Two stays clash exactly when they share a covered day, so one
    # row per day forbids every clash. The row for a day is a clique over the requests covering it,
    # a tighter relaxation than one row per clashing pair. A day covered by one request needs no
    # row: its binary variables already keep that request to one room.
    for day in range(min(starts), max(ends)):
        covering = [i for i in range(n) if starts[i] <= day < ends[i]]
        if len(covering) >= 2:
            model.addMatrixCons(x[covering].sum(axis=0) <= 1)

    # room_assignments[i] is the room of request i: the room r for which x[i, r] is 1.
    room_of = x @ np.arange(max_rooms)

    # Satisfaction problem: no objective, any assignment that meets the constraints is a solution.
    return model, {"room_assignments": room_of}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
