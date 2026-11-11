# room_assignment: a PyCSP3 model from DCP Rosetta.
# Download the `room_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python room_assignment.py room_assignment.json

from pycsp3 import *


def create_model(instance):
    """Requests are assigned to a limited number of rooms, one room per request for its whole
    stay. A room serves one request at a time, and a request occupies its room from its start
    date up to, but not including, its end date. Some requests already have a room."""
    start_data = instance["start_data"]                        # start_data[i]: first day of request i, as YYYY-MM-DD text
    end_data = instance["end_data"]                            # end_data[i]: day request i ends (not occupied), as YYYY-MM-DD text
    preassigned_room_data = instance["preassigned_room_data"]  # preassigned_room_data[i]: room of request i, -1 when it has none
    max_rooms = instance["max_rooms"]                          # the rooms are numbered 0 to max_rooms - 1
    n_requests = len(start_data)

    # room_assignments[i] is the room that serves request i
    room_assignments = VarArray(size=n_requests, dom=range(max_rooms))

    # Each request is in one of the rooms 0 to max_rooms - 1. The domain already says so; this
    # constraint is posted because ACE only reports variables that some constraint mentions.
    satisfy([room_assignments[i] < max_rooms for i in range(n_requests)])

    # A request with a pre-assigned room (not -1) is in that room.
    satisfy([room_assignments[i] == preassigned_room_data[i] for i in range(n_requests) if preassigned_room_data[i] >= 0])

    # Requests i and j overlap when each starts before the other ends. ISO dates compare in
    # calendar order as plain text, so the strings are compared directly.
    overlapping_pairs = [
        (i, j)
        for i in range(n_requests)
        for j in range(i + 1, n_requests)
        if start_data[i] < end_data[j] and start_data[j] < end_data[i]
    ]

    # Overlapping requests are in different rooms.
    satisfy([room_assignments[i] != room_assignments[j] for i, j in overlapping_pairs])

    return {"room_assignments": room_assignments}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
