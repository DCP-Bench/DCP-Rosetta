# finding_celebrities: a CPMpy model from DCP Rosetta.
# Download the `finding_celebrities.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python finding_celebrities.py finding_celebrities.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """At a party, a celebrity is a person that everybody knows but that only
    knows other celebrities. Find the celebrities; at least one is present."""
    # graph[i][j] is 1 when person i knows person j
    graph = np.array(instance["graph"])
    n = len(graph)

    # celebrities[i] is true when person i is a celebrity
    celebrities = cp.boolvar(shape=n, name="celebrities")
    # The number of celebrities, at least one
    num_celebrities = cp.intvar(1, n, name="num_celebrities")

    model = cp.Model()
    model.add(num_celebrities == cp.sum(celebrities))

    # Person i is a celebrity exactly when everybody knows them and they know
    # only celebrities. A celebrity knows every celebrity (everybody knows
    # them), so knowing only celebrities means knowing exactly num_celebrities
    # people. The graph is fixed data, so both counts are plain numbers.
    known_by = graph.sum(axis=0)  # known_by[i]: how many people know person i
    knows = graph.sum(axis=1)     # knows[i]: how many people person i knows
    for i in range(n):
        model.add(celebrities[i] == (cp.BoolVal(bool(known_by[i] == n))
                                    & (int(knows[i]) == num_celebrities)))

    return model, {"celebrities": celebrities}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
