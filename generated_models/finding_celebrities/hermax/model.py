# finding_celebrities: a hermax (Python) model from DCP Rosetta.
# Download the `finding_celebrities.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
# Then run it on the first instance (after `pip install hermax`):
#   python finding_celebrities.py finding_celebrities.json

from hermax.model import Model


def create_model(instance):
    """Find the celebrities at a party. Guest i knows guest j when graph[i][j] is 1.
    A celebrity is known by everybody at the party (including by themselves) and
    knows only other celebrities. At least one celebrity is present. Report, for
    each guest in input order, whether they are a celebrity."""
    graph = instance["graph"]  # graph[i][j] = 1 when guest i knows guest j, else 0
    n = len(graph)             # the number of guests at the party

    m = Model()

    # celebrities[i] is true when guest i is a celebrity
    celebrities = m.bool_vector("celebrities", n)

    # Everybody knows a celebrity: a guest whom some guest does not know is not a celebrity.
    for i in range(n):
        for j in range(n):
            if graph[j][i] == 0:
                m &= ~celebrities[i]

    # A celebrity knows only other celebrities: if guest i is a celebrity and knows
    # guest j, then guest j is a celebrity too.
    for i in range(n):
        for j in range(n):
            if i != j and graph[i][j] == 1:
                m &= (~celebrities[i] | celebrities[j])

    # At least one celebrity is present at the party.
    m &= celebrities.at_least_one()

    # The task is satisfaction only: no objective to optimise.
    return m, {"celebrities": celebrities}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
