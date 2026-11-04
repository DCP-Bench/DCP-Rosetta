# room_assignment: an Exact (Python) model from DCP Rosetta.
# Download the `room_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python room_assignment.py room_assignment.json

from datetime import date

from exact import Exact


def create_model(instance):
    """Give every booking, a stay from a start date up to, but not including, an end date,
    one room for its whole stay, so that no room hosts two bookings on the same night.
    Some bookings already have their room fixed."""
    n_rooms = instance["max_rooms"]                                    # the number of rooms, numbered 0 .. n_rooms - 1
    starts = [date.fromisoformat(d) for d in instance["start_data"]]   # starts[i]: first night of booking i
    ends = [date.fromisoformat(d) for d in instance["end_data"]]       # ends[i]: day booking i ends, the room is free from then on
    preassigned = instance["preassigned_room_data"]                    # preassigned[i]: the room fixed for booking i, -1 when none
    n_bookings = len(starts)

    solver = Exact()

    # Exact identifies its variables by name.
    # room_assignments[i] is the room given to booking i
    room_assignments = [f"room_{i}" for i in range(n_bookings)]
    # in_room[i][r] is 1 when booking i is in room r, and 0 otherwise
    in_room = [[f"booking_{i}_in_{r}" for r in range(n_rooms)] for i in range(n_bookings)]
    for i in range(n_bookings):
        solver.addVariable(room_assignments[i], 0, n_rooms - 1)
        for r, name in enumerate(in_room[i]):
            # a fixed room is the only room the booking can be in
            solver.addVariable(name, 1 if preassigned[i] == r else 0, 1)
        # each booking is in exactly one room
        solver.addConstraint([(1, name) for name in in_room[i]], True, 1, True, 1)
        # the room number of booking i is the number of the room it is in
        solver.addConstraint([(r, in_room[i][r]) for r in range(1, n_rooms)] + [(-1, room_assignments[i])],
                             True, 0, True, 0)

    # two bookings that share a night are in different rooms
    for i in range(n_bookings):
        for j in range(i + 1, n_bookings):
            if max(starts[i], starts[j]) < min(ends[i], ends[j]):
                for r in range(n_rooms):
                    solver.addConstraint([(1, in_room[i][r]), (1, in_room[j][r])], False, 0, True, 1)

    return solver, {"room_assignments": room_assignments}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
