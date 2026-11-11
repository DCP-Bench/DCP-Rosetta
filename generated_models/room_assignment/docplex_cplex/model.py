# room_assignment: a CPLEX (Python) model from DCP Rosetta.
# Download the `room_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python room_assignment.py room_assignment.json

from datetime import date, timedelta
from docplex.mp.model import Model


def create_model(instance):
    """Assign every request one room for its entire duration, keeping the room some requests already
    have, so that no room serves two requests at the same time. A request occupies its room from its
    start date up to, but not including, its end date."""
    max_rooms = instance["max_rooms"]                    # rooms are numbered 0..max_rooms-1
    starts = [date.fromisoformat(s) for s in instance["start_data"]]  # starts[i]: first day of request i
    ends = [date.fromisoformat(e) for e in instance["end_data"]]      # ends[i]: end date of request i, not occupied
    preassigned = instance["preassigned_room_data"]      # -1: no room given in advance
    requests = range(len(starts))
    rooms = range(max_rooms)

    model = Model("room_assignment")

    # in_room[i, r] is 1 when request i gets room r
    in_room = {(i, r): model.binary_var(name=f"in_room_{i}_{r}") for i in requests for r in rooms}

    # Every request is assigned to exactly one room.
    model.add_constraints(model.sum(in_room[i, r] for r in rooms) == 1 for i in requests)

    # A request with a room assigned in advance keeps that room.
    for i in requests:
        if preassigned[i] != -1:
            if preassigned[i] in rooms:
                model.add_constraint(in_room[i, preassigned[i]] == 1)
            else:
                # a pre-assigned room that does not exist cannot be given: the instance is infeasible
                model.add_constraint(model.sum(in_room[i, r] for r in rooms) == 0)

    # A room can serve only one request at a time: a request occupies the days from its start
    # up to, not including, its end, and the requests present on the same day get different
    # rooms. Each distinct group of requests sharing a day is posted once.
    groups = set()
    for i in requests:
        day = starts[i]
        while day < ends[i]:
            present = tuple(k for k in requests if starts[k] <= day < ends[k])
            if len(present) > 1:
                groups.add(present)
            day += timedelta(days=1)
    for present in sorted(groups):
        for r in rooms:
            model.add_constraint(model.sum(in_room[k, r] for k in present) <= 1)

    # room_assignments[i] is the number of the room of request i
    room_assignments = [model.sum(r * in_room[i, r] for r in rooms) for i in requests]
    return model, {"room_assignments": room_assignments}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
