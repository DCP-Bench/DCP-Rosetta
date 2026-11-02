# among: a PuLP (Python) model from DCP Rosetta.
# Download the `among.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python among.py among.json

import pulp


def create_model(instance):
    """Fill a list of n positions with values from 0 to 7 so that exactly m of the
    positions take a value from v."""
    n_values = instance["n"]      # the number of positions in x
    n_matches = instance["m"]     # how many positions must take a value from v
    v = instance["v"]             # the values that count as a match

    # The values a position may take, 0 to 7.
    domain = range(8)

    problem = pulp.LpProblem("among", pulp.LpMinimize)

    # x[i]: the value at position i
    x = [pulp.LpVariable(f"x_{i}", domain[0], domain[-1], cat="Integer") for i in range(n_values)]

    # takes[i][d] is 1 when x[i] is d.
    takes = [{d: pulp.LpVariable(f"takes_{i}_{d}", cat="Binary") for d in domain}
             for i in range(n_values)]

    for i in range(n_values):
        # Each position takes exactly one value, and x[i] is that value.
        problem += pulp.lpSum(takes[i].values()) == 1
        problem += x[i] == pulp.lpSum(d * takes[i][d] for d in domain)

    # Exactly n_matches positions take a value from v.
    problem += pulp.lpSum(takes[i][d] for i in range(n_values) for d in v) == n_matches

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
