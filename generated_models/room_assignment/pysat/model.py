# room_assignment: a PySAT (Python) model from DCP Rosetta.
# Download the `room_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python room_assignment.py room_assignment.json

from datetime import date

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Assign each request, a stay from a start date up to, but not including, an end date,
    to one room for its whole stay, so that a room never serves two requests at once. Some
    requests already have a room."""
    max_rooms = instance["max_rooms"]                                                # the number of rooms, numbered 0 .. max_rooms - 1
    starts = [date.fromisoformat(d) for d in instance["start_data"]]                 # starts[i]: the first day of request i
    ends = [date.fromisoformat(d) for d in instance["end_data"]]                     # ends[i]: the day request i ends, when its room is free again
    preassigned = instance["preassigned_room_data"]                                  # preassigned[i]: the room request i already has, -1 if none
    n_requests = len(starts)  # the number of requests

    # Every variable of the model comes from this pool.
    pool = IDPool()
    # room_assignments[i]: the room request i stays in
    room_assignments = [Integer(f"room_{i}", 0, max_rooms - 1, vpool=pool) for i in range(n_requests)]
    # The whole-number variables above. The constraints below are added to the model.
    engine = IntegerEngine(vars=room_assignments, vpool=pool)
    cnf = engine.clausify()

    # Requests that already have a room keep it.
    for i in range(n_requests):
        if preassigned[i] != -1:
            cnf.append([room_assignments[i].equals(preassigned[i])])

    # A room serves one request at a time, so two requests that both cover some day need different rooms.
    for i in range(n_requests):
        for j in range(i + 1, n_requests):
            if max(starts[i], starts[j]) < min(ends[i], ends[j]):
                for room in range(max_rooms):
                    cnf.append([-room_assignments[i].equals(room), -room_assignments[j].equals(room)])

    return cnf, {"room_assignments": room_assignments}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
