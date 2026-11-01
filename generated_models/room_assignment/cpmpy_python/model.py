# room_assignment: a CPMpy model from DCP Rosetta.
# Download the `room_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python room_assignment.py room_assignment.json

from datetime import date, timedelta

import cpmpy as cp


def create_model(instance):
    """Assign each request (a stay from a start date up to, but not including, an end
    date) to one room for its whole stay, so that a room never serves two requests at
    once. Some requests already have a room."""
    max_rooms = instance["max_rooms"]                                    # the number of rooms, numbered 0 .. max_rooms - 1
    starts = [date.fromisoformat(d) for d in instance["start_data"]]     # starts[i]: first day of request i
    ends = [date.fromisoformat(d) for d in instance["end_data"]]         # ends[i]: day request i ends (the room is free again that day)
    preassigned = instance["preassigned_room_data"]                      # preassigned[i]: room fixed for request i, -1 if none

    # room[i] is the room that request i stays in
    room = cp.intvar(0, max_rooms - 1, shape=(len(starts),), name="room")

    model = cp.Model()
    # Requests that already have a room keep it.
    for i, fixed_room in enumerate(preassigned):
        if fixed_room != -1:
            model.add(room[i] == fixed_room)

    # A room serves one request at a time: the requests occupying a given day
    # (start <= day < end) must all be in different rooms.
    day = min(starts)
    while day <= max(ends):
        on_this_day = [i for i in range(len(starts)) if starts[i] <= day < ends[i]]
        if len(on_this_day) > 1:
            model.add(cp.AllDifferent(room[on_this_day]))
        day += timedelta(days=1)

    return model, {"room_assignments": room}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
