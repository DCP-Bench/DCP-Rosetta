# room_assignment: a FOX model for GroundFOX from DCP Rosetta.
#
# The room assignment problem involves assigning a set of requests to a limited number of
# rooms such that each request is assigned to one room for its entire duration. Some requests
# may already have a room pre-assigned. The main constraint is that a room can only serve one
# request at a time, meaning no overlapping requests can be assigned to the same room. A
# request occupies its room from its start date up to, but not including, its end date, so one
# request can start in a room on the day another ends there. A pre-assigned room of -1 means
# that the request has none.
#
# Print the room assignment for each request (room_assignments) as a list of integers ranging
# from 0 to max_rooms - 1.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py room_assignment.json --check

# room_assignment: a FOX model for GroundFOX from DCP Rosetta.

FOX = """
invocabulary { Req/1 Room/1 Clash/2 Fixed/2 }
outvocabulary { room_assignments/2 }
theory {
    ! i [Req(i)] : ? r [Room(r)] : room_assignments(i, r).
    ! i [Req(i)] : ! r [Room(r)] : ! s [Room(s) & r ~= s] : ~room_assignments(i, r) | ~room_assignments(i, s).
    ! i [Req(i)] : ! j [Clash(i, j)] : ! r [Room(r)] : ~room_assignments(i, r) | ~room_assignments(j, r).
    ! i [Req(i)] : ! r [Fixed(i, r)] : room_assignments(i, r).
}
"""

from datetime import datetime

_FORMATS = ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y%m%d")


def _parse(text):
    s = text.strip()
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        pass
    for fmt in _FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError("unrecognised date: " + repr(text))


def structure(instance):
    starts = [_parse(s) for s in instance["start_data"]]
    ends = [_parse(s) for s in instance["end_data"]]
    n = len(starts)
    R = instance["max_rooms"]
    # Requests i and j clash when their half-open intervals [start, end) overlap.
    clash = [(i, j) for i in range(n) for j in range(n)
             if i != j and starts[i] < ends[j] and starts[j] < ends[i]]
    fixed = [(i, r) for i, r in enumerate(instance["preassigned_room_data"]) if r >= 0]
    return {
        "Req": range(n),
        "Room": range(R),
        "Clash": clash,
        "Fixed": fixed,
    }
