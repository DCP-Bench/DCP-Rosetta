# car_selection: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `car_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
# Then run it on the first instance (after `pip install ortools`):
#   python car_selection.py car_selection.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Participants are assigned to cars. Each participant is interested in some of the cars and
    gets at most one of them, and each car goes to at most one participant. Maximize the number
    of assignments."""
    # possible[i][j] is 1 when participant i is interested in car j
    possible = instance["possible_assignments"]
    # the number of participants and the number of cars
    n_participants, n_cars = len(possible), len(possible[0])

    model = cp_model.CpModel()

    # assigned[i][j] is true when participant i gets car j
    assigned = [
        [model.new_bool_var(f"a_{i}_{j}") for j in range(n_cars)] for i in range(n_participants)
    ]

    # A participant only gets a car they are interested in.
    for i in range(n_participants):
        for j in range(n_cars):
            model.add(assigned[i][j] <= possible[i][j])
    # Each participant gets at most one car.
    for i in range(n_participants):
        model.add_at_most_one(assigned[i])
    # Each car goes to at most one participant.
    for j in range(n_cars):
        model.add_at_most_one(assigned[i][j] for i in range(n_participants))

    # Maximize the number of assignments.
    model.maximize(sum(assigned[i][j] for i in range(n_participants) for j in range(n_cars)))

    return model, {"assignments": assigned}


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
