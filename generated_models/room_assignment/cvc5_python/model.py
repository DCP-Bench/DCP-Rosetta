# room_assignment: a cvc5 (Python) model from DCP Rosetta.
# Download the `room_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python room_assignment.py room_assignment.json

from datetime import date

import cvc5.pythonic as c5


# the day number of an ISO date text, so that dates can be compared and subtracted
def _day(text):
    return date.fromisoformat(text).toordinal()


def create_model(instance):
    """Assign each request to one room for its whole stay, so that no room serves two
    stays that overlap. Some requests already have a room."""
    max_rooms = instance["max_rooms"]                    # the number of rooms, numbered 0 to max_rooms - 1
    starts = [_day(s) for s in instance["start_data"]]  # starts[i]: the day request i starts
    ends = [_day(e) for e in instance["end_data"]]      # ends[i]: the day request i leaves, when its room is free again
    preassigned = instance["preassigned_room_data"]     # preassigned[i]: the room request i already has, -1 if none
    n_requests = len(starts)

    # room[i] is the room that request i stays in
    room = [c5.Int(f"room_{i}") for i in range(n_requests)]

    solver = c5.Solver()

    # Each request is in a room from 0 to max_rooms - 1.
    for i in range(n_requests):
        solver.add(room[i] >= 0)
        solver.add(room[i] <= max_rooms - 1)

    # Requests that already have a room keep it.
    for i in range(n_requests):
        if preassigned[i] >= 0:
            solver.add(room[i] == preassigned[i])

    # Two stays that overlap cannot share a room.
    for i in range(n_requests):
        for j in range(i + 1, n_requests):
            if starts[i] < ends[j] and starts[j] < ends[i]:
                solver.add(room[i] != room[j])

    return solver, {"room_assignments": room}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
