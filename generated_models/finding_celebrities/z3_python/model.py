# finding_celebrities: a Z3 (Python) model from DCP Rosetta.
# Download the `finding_celebrities.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python finding_celebrities.py finding_celebrities.json

import z3


def create_model(instance):
    """At a party, a celebrity is a person whom everybody knows and who knows only
    celebrities. Find who the celebrities are; at least one is present."""
    graph = instance["graph"]  # graph[i][j] is 1 when person i knows person j
    n_people = len(graph)      # the number of people at the party

    # celebrities[i] is true when person i is a celebrity
    celebrities = [z3.Bool(f"celebrities_{i}") for i in range(n_people)]
    # the number of celebrities
    n_celebrities = z3.Int("n_celebrities")

    solver = z3.Solver()

    # Count the celebrities; at least one is present.
    solver.add(
        n_celebrities == z3.Sum([z3.If(c, 1, 0) for c in celebrities]),
        n_celebrities >= 1,
        n_celebrities <= n_people,
    )

    # A person is a celebrity when everybody knows them and they know as many
    # people as there are celebrities, so that they know only celebrities.
    for i in range(n_people):
        known_by = sum(graph[j][i] for j in range(n_people))  # how many people know person i
        knows = sum(graph[i])                                 # how many people person i knows
        solver.add(celebrities[i] == z3.And(z3.BoolVal(known_by == n_people),
                                            n_celebrities == knows))

    return solver, {"celebrities": celebrities}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
