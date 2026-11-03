# csplib_074_maximum_clique: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_074_maximum_clique.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_074_maximum_clique.py csplib_074_maximum_clique.json

import pulp


def create_model(instance):
    """In a simple undirected graph, find a clique (a set of vertices that are all pairwise
    adjacent) of the largest possible size."""
    n = instance["n"]      # number of vertices
    adj = instance["adj"]  # adj[i][j]: 1 when vertices i and j are joined by an edge, 0 when not

    problem = pulp.LpProblem("maximum_clique", pulp.LpMaximize)

    # c[i] is 1 when vertex i is in the clique, and 0 when not
    c = [pulp.LpVariable(f"c_{i}", cat="Binary") for i in range(n)]

    # Two vertices that are not joined by an edge cannot both be in the clique.
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j] == 0:
                problem += c[i] + c[j] <= 1

    # The clique has as many vertices as possible.
    problem += pulp.lpSum(c)

    return problem, {"c": c}


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
