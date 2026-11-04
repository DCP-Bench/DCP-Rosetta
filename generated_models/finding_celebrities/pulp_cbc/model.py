# finding_celebrities: a PuLP (Python) model from DCP Rosetta.
# Download the `finding_celebrities.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python finding_celebrities.py finding_celebrities.json

import pulp


def create_model(instance):
    """At a party, a celebrity is a person that everybody knows but that only
    knows other celebrities. Find the celebrities; at least one is present."""
    graph = instance["graph"]  # graph[i][j] is 1 when person i knows person j
    n = len(graph)             # the number of people at the party

    problem = pulp.LpProblem("finding_celebrities", pulp.LpMinimize)

    # celebrities[i] is 1 when person i is a celebrity
    celebrities = [pulp.LpVariable(f"celebrities_{i}", cat="Binary") for i in range(n)]
    # num_is[v] is 1 when there are exactly v celebrities, for v from 1 to n
    num_is = {v: pulp.LpVariable(f"num_is_{v}", cat="Binary") for v in range(1, n + 1)}

    # The number of celebrities is one of 1 to n, and it equals the number of people marked as celebrities.
    problem += pulp.lpSum(num_is.values()) == 1
    problem += pulp.lpSum(celebrities) == pulp.lpSum(v * num_is[v] for v in range(1, n + 1))

    # A person is a celebrity exactly when everybody knows them and they know as many people
    # as there are celebrities, since the celebrities know only each other. A person whom
    # somebody at the party does not know is no celebrity.
    for i in range(n):
        known_by = sum(graph[j][i] for j in range(n))  # how many people know person i
        knows = sum(graph[i])                          # how many people person i knows
        if known_by == n and knows >= 1:
            problem += celebrities[i] == num_is[knows]
        else:
            problem += celebrities[i] == 0

    return problem, {"celebrities": celebrities}


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
