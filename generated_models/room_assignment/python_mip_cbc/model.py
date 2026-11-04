# room_assignment: a Python-MIP (Python) model from DCP Rosetta.
# Download the `room_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python room_assignment.py room_assignment.json

import mip
from datetime import date


def create_model(instance):
    """Assign each request (a stay from a start date up to, but not including, an end
    date) to one room for its whole stay, so that a room never serves two requests at
    once. Some requests already have a room."""
    max_rooms = instance["max_rooms"]                                             # the number of rooms, numbered 0 .. max_rooms - 1
    starts = [date.fromisoformat(s).toordinal() for s in instance["start_data"]]  # starts[i]: first day of request i, as a day number
    ends = [date.fromisoformat(s).toordinal() for s in instance["end_data"]]      # ends[i]: day request i ends, when its room is free again
    preassigned = instance["preassigned_room_data"]                               # preassigned[i]: room fixed for request i, -1 if none
    n_requests = len(starts)                                                      # number of requests

    model = mip.Model(solver_name="CBC")

    # in_room[i][r] is 1 when request i is in room r, and 0 when not
    in_room = [[model.add_var(f"in_room_{i}_{r}", var_type=mip.BINARY) for r in range(max_rooms)]
               for i in range(n_requests)]
    # room[i]: the room number of request i
    room = [model.add_var(f"room_{i}", lb=0, ub=max_rooms - 1, var_type=mip.INTEGER)
            for i in range(n_requests)]

    # Each request is in exactly one room.
    for i in range(n_requests):
        model += mip.xsum(in_room[i]) == 1

    # The room number of each request is the room it is in.
    for i in range(n_requests):
        model += room[i] == mip.xsum(r * in_room[i][r] for r in range(max_rooms))

    # A request with a preassigned room stays in it.
    for i in range(n_requests):
        if preassigned[i] >= 0:
            model += in_room[i][preassigned[i]] == 1

    # Two requests that overlap in time cannot share a room.
    for i in range(n_requests):
        for j in range(i + 1, n_requests):
            if starts[i] < ends[j] and starts[j] < ends[i]:
                for r in range(max_rooms):
                    model += in_room[i][r] + in_room[j][r] <= 1

    # On each day, the requests occupying that day are in different rooms. One row per day and room.
    if n_requests > 0:
        for d in range(min(starts), max(ends)):
            occupying = [i for i in range(n_requests) if starts[i] <= d < ends[i]]  # requests occupying day d
            if len(occupying) > 1:
                for r in range(max_rooms):
                    model += mip.xsum(in_room[i][r] for i in occupying) <= 1

    return model, {"room_assignments": room}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
