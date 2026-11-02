# autoref: a PuLP (Python) model from DCP Rosetta.
# Download the `autoref.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python autoref.py autoref.json

import pulp


def create_model(instance):
    """Find a series s[0], s[1], ..., s[n+1] in which every integer i from 0 to n
    occurs exactly s[i] times, and whose last element s[n+1] equals m."""
    n = instance["n"]  # the values 0 to n are counted in the series
    m = instance["m"]  # the required value of the last element

    problem = pulp.LpProblem("autoref", pulp.LpMinimize)

    n_elements = n + 2  # the series has the elements s[0] to s[n+1]

    # s[j] is the value of element j, a number from 0 to n
    s = [pulp.LpVariable(f"s_{j}", 0, n, cat="Integer") for j in range(n_elements)]

    # holds[j][v] is 1 when element j of the series has the value v, and 0 when not
    holds = [[pulp.LpVariable(f"holds_{j}_{v}", cat="Binary") for v in range(n + 1)]
             for j in range(n_elements)]

    # Each element has exactly one value, and s[j] is that value.
    for j in range(n_elements):
        problem += pulp.lpSum(holds[j]) == 1
        problem += s[j] == pulp.lpSum(v * holds[j][v] for v in range(n + 1))

    # The value i occurs exactly s[i] times in the series, for i from 0 to n.
    for i in range(n + 1):
        problem += s[i] == pulp.lpSum(holds[j][i] for j in range(n_elements))

    # The last element is m.
    problem += s[n + 1] == m

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
