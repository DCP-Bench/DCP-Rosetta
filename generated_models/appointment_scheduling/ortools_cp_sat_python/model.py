# appointment_scheduling: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `appointment_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
# Then run it on the first instance (after `pip install ortools`):
#   python appointment_scheduling.py appointment_scheduling.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Schedule people into interview slots based on their free-busy schedules:
    every person gets exactly one slot in which they are free, and every slot
    gets exactly one person."""
    free = instance["m"]     # free[i][j] is true when person i is free in slot j
    n_people = len(free)     # the number of people, which is also the number of slots

    model = cp_model.CpModel()

    # booked[i][j] is true when person i is assigned to slot j
    booked = [[model.new_bool_var(f"x_{i}_{j}") for j in range(n_people)] for i in range(n_people)]

    # Each person is assigned to exactly one slot, and that slot is one they are free in.
    for i in range(n_people):
        model.add(sum(free[i][j] * booked[i][j] for j in range(n_people)) == 1)
        model.add_exactly_one(booked[i])
    # Each slot gets exactly one person.
    for j in range(n_people):
        model.add_exactly_one(booked[i][j] for i in range(n_people))

    return model, {"x": booked}


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
