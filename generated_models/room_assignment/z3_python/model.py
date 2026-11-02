# room_assignment: a Z3 (Python) model from DCP Rosetta.
# Download the `room_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python room_assignment.py room_assignment.json

import datetime

import z3


def create_model(instance):
    """Assign each request, a stay from a start date up to an end date, to one room for its
    whole stay, so that a room never serves two requests at once. Some requests already
    have a room."""
    max_rooms = instance["max_rooms"]                                           # the number of rooms, numbered 0 .. max_rooms - 1
    starts = [datetime.date.fromisoformat(s) for s in instance["start_data"]]   # starts[i]: first day of request i
    ends = [datetime.date.fromisoformat(e) for e in instance["end_data"]]       # ends[i]: day request i ends, when its room is free again
    preassigned = instance["preassigned_room_data"]                             # preassigned[i]: room fixed for request i, or -1 if none
    n_requests = len(starts)

    # room[i] is the room that request i stays in
    room = [z3.Int(f"room_{i}") for i in range(n_requests)]

    solver = z3.Solver()

    solver.add(
        # Each request gets one of the rooms.
        *[z3.And(room[i] >= 0, room[i] <= max_rooms - 1) for i in range(n_requests)],
        # Requests that already have a room keep it.
        *[room[i] == preassigned[i] for i in range(n_requests) if preassigned[i] != -1],
    )

    if n_requests > 0:
        # groups: the sets of requests that stay on the same day (a request stays from its
        # start day up to, not including, its end day)
        groups = set()
        day = min(starts)
        while day <= max(ends):
            active = tuple(i for i in range(n_requests) if starts[i] <= day < ends[i])
            if len(active) > 1:
                groups.add(active)
            day += datetime.timedelta(days=1)
        # Requests that stay on the same day are in different rooms.
        solver.add([z3.Distinct([room[i] for i in active]) for active in sorted(groups)])

    return solver, {"room_assignments": room}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
