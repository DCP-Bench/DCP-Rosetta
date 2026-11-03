# finding_celebrities: a SCIP (Python) model from DCP Rosetta.
# Download the `finding_celebrities.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python finding_celebrities.py finding_celebrities.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Find the celebrities at a party. A celebrity is a guest whom everybody else
    at the party knows, and who knows only other celebrities. At least one
    celebrity is present."""
    graph = instance["graph"]  # graph[i][j] = 1 when guest i knows guest j
    n = len(graph)             # the number of guests, read from the data

    model = Model("finding_celebrities")

    # celeb[c] is 1 when guest c is a celebrity, and 0 when not
    celeb = [model.addVar(f"celeb_{c}", vtype="B") for c in range(n)]

    # At least one celebrity is present at the party.
    model.addCons(quicksum(celeb) >= 1)

    # Only the entries graph[i][j] with i != j are read: "everybody else" and
    # "the guests c knows" both leave out c itself.
    for c in range(n):
        # A guest that someone else does not know cannot be a celebrity.
        if not all(graph[i][c] == 1 for i in range(n) if i != c):
            model.addCons(celeb[c] == 0)
            continue

        # Everybody else knows c, so c is a celebrity exactly when the guests
        # c knows are all celebrities. SCIP's and-constraint states this in both
        # directions: celeb[c] is 1 only if every known guest is one, and it
        # is 1 whenever every known guest is one.
        known = [j for j in range(n) if j != c and graph[c][j] == 1]
        if known:
            model.addConsAnd([celeb[j] for j in known], celeb[c])
        else:
            # c knows nobody else, so "knows only celebrities" holds trivially.
            model.addCons(celeb[c] == 1)

    return model, {"celebrities": celeb}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
