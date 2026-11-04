# mario: a PuLP (Python) model from DCP Rosetta.
# Download the `mario.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python mario.py mario.json

import pulp


def create_model(instance):
    """Mario collects as much gold as possible by visiting houses. He starts at Mario's house,
    drives between houses on a route, and ends at Luigi's house. The route uses at most the
    fuel he has."""
    n = instance["nHouses"]             # the number of houses
    mario = instance["marioHouse"]      # the house Mario starts from
    luigi = instance["luigiHouse"]      # the house Mario ends at
    fuel_limit = instance["fuelLimit"]  # the most fuel the route may use
    arc_fuel = instance["arc_fuel"]     # arc_fuel[i][j] is the fuel to drive from house i to house j
    gold = instance["goldInHouse"]      # the gold in each house

    problem = pulp.LpProblem("mario", pulp.LpMaximize)

    # go[i][j] is 1 when Mario drives straight from house i to house j. A house off the route
    # is driven to from itself.
    go = pulp.LpVariable.dicts("go", (range(n), range(n)), cat="Binary")
    # Every house is left by one drive and entered by one drive.
    for i in range(n):
        problem += pulp.lpSum(go[i][j] for j in range(n)) == 1
        problem += pulp.lpSum(go[j][i] for j in range(n)) == 1

    # s[i] is the house Mario drives to after house i, or i itself if house i is not on the route
    s = [pulp.LpVariable(f"s_{i}", 0, n - 1, cat="Integer") for i in range(n)]
    for i in range(n):
        problem += s[i] == pulp.lpSum(j * go[i][j] for j in range(n))

    # The route ends with the drive from Luigi's house back to Mario's house.
    problem += go[luigi][mario] == 1

    # order[i] is the place of house i along the route, counted from 1 at Mario's house.
    # When Mario drives from house i to house j, house j comes one place after house i. The
    # places run from 1 to n, so a drive that is not made relaxes the constraint by n - 1.
    # This keeps a loop that misses Mario's house from getting places that rise all the way round.
    order = [pulp.LpVariable(f"order_{i}", 1, 1 if i == mario else n) for i in range(n)]
    for i in range(n):
        for j in range(n):
            if j != i and j != mario:
                problem += order[j] >= order[i] + 1 - (n - 1) * (1 - go[i][j])

    # The drives on the route, the drive back to Mario's house included, use no more than
    # the fuel limit.
    problem += pulp.lpSum(arc_fuel[i][j] * go[i][j] for i in range(n) for j in range(n)) \
        <= fuel_limit

    # The gold collected: the gold of every house on the route.
    problem += pulp.lpSum(gold[i] * (1 - go[i][i]) for i in range(n))

    return problem, {"s": s}


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
