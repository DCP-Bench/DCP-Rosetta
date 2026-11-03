# car_selection: a Python-MIP (Python) model from DCP Rosetta.
# Download the `car_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python car_selection.py car_selection.json

import mip


def create_model(instance):
    """Participants are assigned to cars. Each participant is interested in some of the cars and
    gets at most one of them, and each car goes to at most one participant. Maximize the number
    of assignments."""
    possible = instance["possible_assignments"]  # possible[i][j] is 1 when participant i is interested in car j
    n_participants = len(possible)               # the number of participants
    n_cars = len(possible[0]) if n_participants > 0 else 0  # the number of cars

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # x[i, j] is 1 when participant i gets car j. There is one such variable for each pair
    # the participant is interested in.
    x = {}
    for i in range(n_participants):
        for j in range(n_cars):
            if possible[i][j] == 1:
                x[i, j] = model.add_var(f"x_{i}_{j}", var_type=mip.BINARY)

    # Each participant gets at most one car.
    for i in range(n_participants):
        # the cars participant i could get
        terms = [x[i, j] for j in range(n_cars) if (i, j) in x]
        if terms:
            model += mip.xsum(terms) <= 1

    # Each car goes to at most one participant.
    for j in range(n_cars):
        # the participants who could get car j
        terms = [x[i, j] for i in range(n_participants) if (i, j) in x]
        if terms:
            model += mip.xsum(terms) <= 1

    # Maximize the number of assignments.
    model.objective = mip.xsum(x.values())

    # assignments[i][j] is the assignment of participant i to car j. A pair the participant is
    # not interested in is never assigned, so its entry is an empty sum.
    assignments = [
        [x[i, j] if (i, j) in x else mip.LinExpr() for j in range(n_cars)]
        for i in range(n_participants)
    ]
    return model, {"assignments": assignments}


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
