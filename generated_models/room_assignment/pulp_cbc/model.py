# room_assignment: a PuLP (Python) model from DCP Rosetta.
# Download the `room_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python room_assignment.py room_assignment.json

from datetime import date

import pulp


def create_model(instance):
    """Assign each request, a stay from a start date up to, but not including, an end date,
    to one room for its whole stay, so that a room serves one request at a time. Some requests
    already have their room."""
    max_rooms = instance["max_rooms"]                                  # number of rooms, numbered 0 .. max_rooms - 1
    starts = [date.fromisoformat(d) for d in instance["start_data"]]   # starts[i]: first day of request i
    ends = [date.fromisoformat(d) for d in instance["end_data"]]       # ends[i]: day request i leaves, when the room is free again
    preassigned = instance["preassigned_room_data"]                    # preassigned[i]: room fixed for request i, -1 if none
    n_requests = len(starts)                                           # number of requests

    problem = pulp.LpProblem("room_assignment", pulp.LpMinimize)

    # in_room[i][k] is 1 when request i stays in room k, and 0 otherwise
    in_room = pulp.LpVariable.dicts("in_room", (range(n_requests), range(max_rooms)), cat="Binary")
    # room_assignments[i]: the room that request i stays in
    room_assignments = [pulp.LpVariable(f"room_{i}", 0, max_rooms - 1, cat="Integer")
                        for i in range(n_requests)]

    # Each request stays in exactly one room, and room_assignments[i] is that room.
    for i in range(n_requests):
        problem += pulp.lpSum(in_room[i][k] for k in range(max_rooms)) == 1
        problem += room_assignments[i] == pulp.lpSum(k * in_room[i][k] for k in range(max_rooms))

    # Requests that already have their room keep it.
    for i in range(n_requests):
        if preassigned[i] != -1:
            problem += room_assignments[i] == preassigned[i]

    # Two requests on the same day need different rooms. Every day shared by several requests is
    # the first day of the request that starts last among them, so checking the first day of
    # every request is enough.
    for day in sorted(set(starts)):
        # present: the requests staying on this day
        present = [i for i in range(n_requests) if starts[i] <= day < ends[i]]
        if len(present) > 1:
            for k in range(max_rooms):
                problem += pulp.lpSum(in_room[i][k] for i in present) <= 1

    return problem, {"room_assignments": room_assignments}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
