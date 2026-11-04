# csplib_016_traffic_lights: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_016_traffic_lights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_016_traffic_lights.py csplib_016_traffic_lights.json

import pulp


def create_model(instance):
    """A four-way junction has four vehicle lights and four pedestrian lights.
    Choose a state for every light so that each pair of neighbouring roads shows a
    safe combination of states."""
    # the safe combinations of light states for two neighbouring roads, each written as
    # (vehicle light, pedestrian light, next road's vehicle light, next road's pedestrian light)
    allowed = instance["allowed_tuples"]

    # There is no objective: any set of states that meets the rule is an answer.
    problem = pulp.LpProblem("traffic_lights", pulp.LpMinimize)

    # vehicle[i] is the state of the vehicle light on road i+1: 0 red, 1 red-yellow, 2 green, 3 yellow
    vehicle = [pulp.LpVariable(f"V{i + 1}", 0, 3, cat="Integer") for i in range(4)]
    # pedestrian[i] is the state of the pedestrian light on road i+1: 0 red, 1 green
    pedestrian = [pulp.LpVariable(f"P{i + 1}", 0, 1, cat="Integer") for i in range(4)]

    # pick[i][k] is 1 when the pair of roads i+1 and i+2 (road 4 is followed by road 1)
    # shows the k-th safe combination, and 0 when not
    pick = pulp.LpVariable.dicts("pick", (range(4), range(len(allowed))), cat="Binary")
    for i in range(4):
        j = (i + 1) % 4
        # the four lights of roads i+1 and i+2
        pair = [vehicle[i], pedestrian[i], vehicle[j], pedestrian[j]]
        # Each pair of neighbouring roads shows one safe combination: pick selects it,
        # and the four lights take its values.
        problem += pulp.lpSum(pick[i][k] for k in range(len(allowed))) == 1
        for position in range(4):
            problem += pair[position] == pulp.lpSum(
                allowed[k][position] * pick[i][k] for k in range(len(allowed)))

    return problem, {"lights": vehicle + pedestrian}


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
