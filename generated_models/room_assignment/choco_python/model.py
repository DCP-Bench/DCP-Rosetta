# room_assignment: a Choco-solver (Python) model from DCP Rosetta.
# Download the `room_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python room_assignment.py room_assignment.json

from datetime import date

from pychoco.model import Model


def create_model(instance):
    """Assign each request, a stay from a start date up to, but not including, an end
    date, to one room for its whole stay, so that a room never serves two requests on
    the same night. Some requests already have a room."""
    max_rooms = instance["max_rooms"]                                  # the number of rooms, numbered 0 .. max_rooms - 1
    starts = [date.fromisoformat(d) for d in instance["start_data"]]   # starts[i]: the first night of request i
    ends = [date.fromisoformat(d) for d in instance["end_data"]]       # ends[i]: the day request i ends, when its room is free again
    preassigned = instance["preassigned_room_data"]                    # preassigned[i]: the room fixed for request i, -1 if none
    n_requests = len(starts)

    model = Model()

    # room_assignments[i]: the room that request i stays in
    room_assignments = [model.intvar(0, max_rooms - 1, name=f"room_{i}") for i in range(n_requests)]

    # Requests that already have a room keep it.
    for i in range(n_requests):
        if preassigned[i] != -1:
            model.arithm(room_assignments[i], "=", preassigned[i]).post()

    # Two requests that share a night need different rooms.
    for i in range(n_requests):
        for j in range(i + 1, n_requests):
            if max(starts[i], starts[j]) < min(ends[i], ends[j]):
                model.arithm(room_assignments[i], "!=", room_assignments[j]).post()

    return model, {"room_assignments": room_assignments}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
