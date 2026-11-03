# room_assignment: a hermax (Python) model from DCP Rosetta.
# Download the `room_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
# Then run it on the first instance (after `pip install hermax`):
#   python room_assignment.py room_assignment.json

from datetime import date

from hermax.model import Model


def create_model(instance):
    """Give every booking one room for its whole stay, so that no room hosts two bookings
    on the same night. A booking covers the nights from its start date up to, but not
    including, its end date. Some bookings already have their room fixed. Find a valid
    assignment of rooms to bookings."""
    n_rooms = instance["max_rooms"]  # the number of rooms; rooms are numbered 0 .. max_rooms - 1
    # starts[i]: the first night of booking i, as a day number
    starts = [date.fromisoformat(d).toordinal() for d in instance["start_data"]]
    # ends[i]: the checkout day of booking i, the first day it no longer covers
    ends = [date.fromisoformat(d).toordinal() for d in instance["end_data"]]
    # preassigned[i]: the room booking i must use, or -1 when no room is fixed
    preassigned = instance["preassigned_room_data"]
    n = len(starts)  # the number of requests

    m = Model()
    # room[i] is the room given to booking i; a pre-assigned request has only its fixed room
    room = [
        m.int(f"room_{i}", p, p) if p != -1 else m.int(f"room_{i}", 0, n_rooms - 1)
        for i, p in enumerate(preassigned)
    ]

    # A room serves one booking at a time: two bookings that share a night must get
    # different rooms. They share a night when the later of their starts comes before
    # the earlier of their ends.
    for i in range(n):
        for j in range(i + 1, n):
            if max(starts[i], starts[j]) < min(ends[i], ends[j]):
                m &= (room[i] != room[j])

    return m, {"room_assignments": room}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
