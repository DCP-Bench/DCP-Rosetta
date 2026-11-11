# finding_celebrities: a PyCSP3 model from DCP Rosetta.
# Download the `finding_celebrities.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python finding_celebrities.py finding_celebrities.json

from pycsp3 import *


def create_model(instance):
    """At a party, a celebrity is a person whom everybody at the party knows, but who
    knows only other celebrities. At least one celebrity is present at the party.
    Find the celebrities."""
    graph = instance["graph"]        # graph[i][j] is 1 when guest i knows guest j, else 0
    n_guests = len(graph)

    # celebrities[i] is 1 when guest i is a celebrity, else 0
    celebrities = VarArray(size=n_guests, dom={0, 1})

    satisfy(
        # Everybody knows a celebrity: a guest can be a celebrity only if every guest knows him or her (as in the instances, a celebrity also knows him- or herself).
        [celebrities[j] <= graph[i][j] for i in range(n_guests) for j in range(n_guests)],
        # A celebrity knows only celebrities: where guest i knows guest j, a celebrity i needs a celebrity j.
        [celebrities[i] <= celebrities[j] for i in range(n_guests) for j in range(n_guests) if graph[i][j] == 1],
        # At least one celebrity is present at the party.
        Sum(celebrities) >= 1,
    )

    return {"celebrities": celebrities}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
