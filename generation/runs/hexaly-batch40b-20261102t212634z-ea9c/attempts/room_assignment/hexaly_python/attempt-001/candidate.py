"""Room assignment: give each request a room for its whole stay, no two overlapping stays in one room."""
from datetime import date

import hexaly.optimizer as hx


def build(instance):
    rooms, pre = instance["max_rooms"], instance["preassigned_room_data"]  # pre[r] = -1 if not pre-assigned
    start = [date.fromisoformat(d).toordinal() for d in instance["start_data"]]
    end = [date.fromisoformat(d).toordinal() for d in instance["end_data"]]
    n = len(start)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    room_assignments = [model.int(0, rooms - 1) for _ in range(n)]

    # Pre-assigned requests keep their room
    for r in range(n):
        if pre[r] != -1:
            model.constraint(room_assignments[r] == pre[r])
    # Two stays that overlap get different rooms; a stay runs from its start day up to its end
    # day, so one ending on the day another starts does not overlap it
    for a in range(n):
        for b in range(a + 1, n):
            if start[a] < end[b] and start[b] < end[a]:
                model.constraint(room_assignments[a] != room_assignments[b])

    return optimizer, {"room_assignments": room_assignments}
