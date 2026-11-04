# car_selection: a PuLP (Python) model from DCP Rosetta.
# Download the `car_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python car_selection.py car_selection.json

import pulp


def create_model(instance):
    """Assign participants to cars to maximize the number of assignments. Each participant may be
    interested in some of the cars and gets at most one of them, and each car goes to at most one
    participant."""
    possible = instance["possible_assignments"]  # possible[i][j] is 1 when participant i is interested in car j
    n_participants = len(possible)               # the number of participants
    n_cars = len(possible[0])                    # the number of cars
    participants, cars = range(n_participants), range(n_cars)

    problem = pulp.LpProblem("car_selection", pulp.LpMaximize)

    # assigned[i][j] is 1 when participant i is assigned car j, and 0 when not
    assigned = [[pulp.LpVariable(f"a_{i}_{j}", cat="Binary") for j in cars] for i in participants]

    # A participant is assigned only a car they are interested in.
    for i in participants:
        for j in cars:
            problem += assigned[i][j] <= possible[i][j]

    # Each participant gets at most one car.
    for i in participants:
        problem += pulp.lpSum(assigned[i]) <= 1

    # Each car goes to at most one participant.
    for j in cars:
        problem += pulp.lpSum(assigned[i][j] for i in participants) <= 1

    # Maximize the number of assignments.
    problem += pulp.lpSum(assigned[i][j] for i in participants for j in cars)

    return problem, {"assignments": assigned}


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
