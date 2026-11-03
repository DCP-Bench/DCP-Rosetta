# appointment_scheduling: a Python-MIP (Python) model from DCP Rosetta.
# Download the `appointment_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python appointment_scheduling.py appointment_scheduling.json

import mip


def create_model(instance):
    """Schedule people into interview slots based on their free-busy schedules:
    each person gets exactly one slot in which they are free, and each slot gets
    at most one person."""
    free = instance["m"]    # free[i][j] is 1 when person i is free in slot j, and 0 when busy
    n_people = len(free)    # the number of people
    n_slots = len(free[0])  # the number of interview slots

    model = mip.Model(solver_name="CBC")

    # x[i][j] is 1 when person i is interviewed in slot j, and 0 when not
    x = [
        [model.add_var(f"x_{i}_{j}", var_type=mip.BINARY) for j in range(n_slots)]
        for i in range(n_people)
    ]

    # Each person is interviewed in exactly one slot.
    for i in range(n_people):
        model += mip.xsum(x[i][j] for j in range(n_slots)) == 1

    # Each slot holds at most one interview.
    for j in range(n_slots):
        model += mip.xsum(x[i][j] for i in range(n_people)) <= 1

    # A person is interviewed only in a slot in which they are free.
    for i in range(n_people):
        for j in range(n_slots):
            model += x[i][j] <= free[i][j]

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
