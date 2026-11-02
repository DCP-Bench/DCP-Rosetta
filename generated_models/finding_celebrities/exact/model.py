# finding_celebrities: an Exact (Python) model from DCP Rosetta.
# Download the `finding_celebrities.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python finding_celebrities.py finding_celebrities.json

from exact import Exact


def create_model(instance):
    """At a party, a celebrity is a person whom everybody knows and who knows only
    other celebrities. Find the celebrities; at least one is present."""
    graph = instance["graph"]  # graph[i][j] is 1 when person i knows person j, and 0 when not
    n = len(graph)             # the number of people at the party

    solver = Exact()

    # Exact identifies its variables by name.
    # celebrities[i] is 1 when person i is a celebrity
    celebrities = [f"celebrity_{i}" for i in range(n)]
    for name in celebrities:
        solver.addVariable(name, 0, 1)

    # num_celebrities is the number of celebrities, at least one
    solver.addVariable("num_celebrities", 1, n)
    # The number of celebrities is the number of people marked as celebrities.
    solver.addConstraint([(1, name) for name in celebrities] + [(-1, "num_celebrities")], True, 0, True, 0)

    # exactly_count[v] is 1 when there are exactly v celebrities, for v from 1 to n
    exactly_count = {v: f"exactly_{v}_celebrities" for v in range(1, n + 1)}
    for name in exactly_count.values():
        solver.addVariable(name, 0, 1)
    # Exactly one of these counts holds.
    solver.addConstraint([(1, name) for name in exactly_count.values()], True, 1, True, 1)
    # The number of celebrities is the count that holds.
    solver.addConstraint([(v, name) for v, name in exactly_count.items()] + [(-1, "num_celebrities")], True, 0, True, 0)

    for i in range(n):
        known_by = sum(graph[j][i] for j in range(n))  # how many people know person i
        knows = sum(graph[i])                          # how many people person i knows
        if known_by == n and knows in exactly_count:
            # Person i is a celebrity exactly when everybody knows i and i knows as many people as there are celebrities.
            solver.addConstraint([(1, celebrities[i]), (-1, exactly_count[knows])], True, 0, True, 0)
        else:
            # Person i is no celebrity: somebody does not know i, or i knows nobody.
            solver.addConstraint([(1, celebrities[i])], True, 0, True, 0)

    return solver, {"celebrities": celebrities}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
