# finding_celebrities: a cvc5 (Python) model from DCP Rosetta.
# Download the `finding_celebrities.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python finding_celebrities.py finding_celebrities.json

import cvc5.pythonic as c5


def create_model(instance):
    """At a party, a celebrity is a person that everybody knows but that only
    knows other celebrities. Find the celebrities; at least one is present."""
    graph = instance["graph"]  # graph[i][j]: whether person i knows person j
    n_people = len(graph)      # the number of people at the party

    # celebrity[i] is true when person i is a celebrity
    celebrity = [c5.Bool(f"celebrity_{i}") for i in range(n_people)]

    solver = c5.Solver()

    # At least one celebrity is present at the party.
    solver.add(c5.Or(celebrity))

    # Person i is no celebrity when somebody at the party does not know them.
    for i in range(n_people):
        if any(graph[j][i] != 1 for j in range(n_people)):
            solver.add(c5.Not(celebrity[i]))

    # A celebrity knows only other celebrities.
    for i in range(n_people):
        for j in range(n_people):
            if graph[i][j] == 1:
                solver.add(c5.Implies(celebrity[i], celebrity[j]))

    return solver, {"celebrities": celebrity}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
