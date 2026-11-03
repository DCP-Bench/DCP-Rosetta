"""Room assignment: give each request a room for its whole stay, no two overlapping stays in one room.

Each request is a stay with a start and an end date. Some requests already have a room.
A room can serve only one request at a time.
"""
from datetime import date

import hexaly.optimizer as hx


def build(instance):
    # max_rooms: number of rooms available
    # preassigned_room_data[r]: room already assigned to request r, -1 if request r has none
    rooms, pre = instance["max_rooms"], instance["preassigned_room_data"]
    # start_data[r]: first day of the stay of request r, an ISO date string (YYYY-MM-DD), turned into a day number
    start = [date.fromisoformat(d).toordinal() for d in instance["start_data"]]
    # end_data[r]: end day of the stay of request r, an ISO date string, turned into a day number
    end = [date.fromisoformat(d).toordinal() for d in instance["end_data"]]
    n = len(start)  # number of requests
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # room_assignments[r] is the room (0 to max_rooms - 1) that request r stays in for its whole duration
    room_assignments = [model.int(0, rooms - 1) for _ in range(n)]

    # Requests that already have a room keep it
    for r in range(n):
        if pre[r] != -1:
            model.constraint(room_assignments[r] == pre[r])
    # A room serves one request at a time: two stays that overlap get different rooms. A stay runs
    # from its start day up to its end day, so one ending on the day another starts does not overlap it
    for a in range(n):
        for b in range(a + 1, n):
            if start[a] < end[b] and start[b] < end[a]:
                model.constraint(room_assignments[a] != room_assignments[b])

    return optimizer, {"room_assignments": room_assignments}
