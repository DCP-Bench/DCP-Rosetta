# session2_color_simple: a PuLP (Python) model from DCP Rosetta.
# Download the `session2_color_simple.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python session2_color_simple.py session2_color_simple.json

import pulp


def create_model(instance):
    """Colour the countries so that two neighbouring countries never share a
    colour, using as few colours as possible. The colours are the integers
    starting from 1."""
    graph = instance["graph"]                        # the pairs of neighbouring countries
    n_countries = max(max(pair) for pair in graph)   # the number of countries
    colours = range(1, n_countries + 1)              # every colour a country could take

    problem = pulp.LpProblem("colouring", pulp.LpMinimize)

    # pick[i][c] is 1 when country i has colour c, and 0 when not
    pick = pulp.LpVariable.dicts("pick", (range(n_countries), colours), cat="Binary")

    # Each country has exactly one colour.
    for i in range(n_countries):
        problem += pulp.lpSum(pick[i][c] for c in colours) == 1

    # Neighbouring countries do not share a colour.
    for first, second in graph:
        for c in colours:
            problem += pick[first - 1][c] + pick[second - 1][c] <= 1

    # colors[i] is the colour number of country i+1
    colors = [pulp.LpVariable(f"colour_{i}", 1, n_countries, cat="Integer")
              for i in range(n_countries)]
    for i in range(n_countries):
        problem += colors[i] == pulp.lpSum(c * pick[i][c] for c in colours)

    # highest is the largest colour number in use.
    highest = pulp.LpVariable("highest", 1, n_countries, cat="Integer")
    for i in range(n_countries):
        problem += highest >= colors[i]

    # Use as few colours as possible: make the highest colour number as small as possible.
    problem += highest

    return problem, {"colors": colors}


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
