# room_assignment: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `room_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
# Then run it on the first instance (after `pip install ortools`):
#   python room_assignment.py room_assignment.json

from datetime import date

from ortools.sat.python import cp_model


def create_model(instance):
    """Assign each request, a stay from a start date to an end date, to one room for its
    whole stay, so that a room never serves two requests at once. Some requests already
    have a room."""
    max_rooms = instance["max_rooms"]                                   # the number of rooms, numbered 0 .. max_rooms - 1
    starts = [date.fromisoformat(d) for d in instance["start_data"]]    # starts[i]: first day of request i
    ends = [date.fromisoformat(d) for d in instance["end_data"]]        # ends[i]: day request i ends (the room is free again that day)
    preassigned = instance["preassigned_room_data"]                     # preassigned[i]: room fixed for request i, -1 if none
    n_requests = len(starts)                                            # the number of requests

    model = cp_model.CpModel()

    # room[i] is the room that request i stays in
    room = [model.new_int_var(0, max_rooms - 1, f"room_{i}") for i in range(n_requests)]

    # Requests that already have a room keep it.
    for i in range(n_requests):
        if preassigned[i] != -1:
            model.add(room[i] == preassigned[i])

    # Two requests that share a night need different rooms.
    for i in range(n_requests):
        for j in range(i + 1, n_requests):
            if max(starts[i], starts[j]) < min(ends[i], ends[j]):
                model.add(room[i] != room[j])

    return model, {"room_assignments": room}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
