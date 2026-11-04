# appointment_scheduling: a PuLP (Python) model from DCP Rosetta.
# Download the `appointment_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python appointment_scheduling.py appointment_scheduling.json

import pulp


def create_model(instance):
    """Schedule people into interview slots based on their free-busy schedules:
    every person gets exactly one slot in which they are free, and every slot
    gets exactly one person."""
    free = instance["m"]    # free[i][j] is 1 when person i is free in slot j
    n_people = len(free)    # the number of people, which is also the number of slots

    problem = pulp.LpProblem("appointment_scheduling", pulp.LpMinimize)

    # x[i][j] is 1 when person i is assigned to slot j, and 0 when not
    x = [[pulp.LpVariable(f"x_{i}_{j}", cat="Binary") for j in range(n_people)]
         for i in range(n_people)]

    for i in range(n_people):
        # Each person has exactly one slot they are free in.
        problem += pulp.lpSum(free[i][j] * x[i][j] for j in range(n_people)) == 1
        # Each person is assigned to exactly one slot.
        problem += pulp.lpSum(x[i]) == 1
        # Each slot is given exactly one person.
        problem += pulp.lpSum(x[j][i] for j in range(n_people)) == 1

    return problem, {"x": x}


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
