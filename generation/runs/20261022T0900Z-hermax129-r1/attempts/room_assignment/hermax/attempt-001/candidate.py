from datetime import date

from hermax.model import Model


def build(instance):
    starts = [date.fromisoformat(s) for s in instance["start_data"]]
    ends = [date.fromisoformat(e) for e in instance["end_data"]]
    preassigned = instance["preassigned_room_data"]
    max_rooms = instance["max_rooms"]
    n = len(starts)

    # Day offsets from the earliest start, so the intervals are small integers.
    origin = min(starts)
    s = [(d - origin).days for d in starts]
    e = [(d - origin).days for d in ends]

    m = Model()
    room = m.int_vector("room", n, 0, max_rooms - 1)

    # Preassigned requests keep their room.
    for i in range(n):
        if preassigned[i] >= 0:
            m &= (room[i] == preassigned[i])

    # A room serves one request at a time. Stays are half-open: the end date
    # is the day of checkout, so a request may check in on the day another
    # checks out. Overlapping requests must use different rooms.
    for i in range(n):
        for j in range(i + 1, n):
            if s[i] < e[j] and s[j] < e[i]:
                m &= (room[i] != room[j])

    return m, {"room_assignments": room}
