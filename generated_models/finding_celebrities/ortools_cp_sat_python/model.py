# finding_celebrities: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `finding_celebrities.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
# Then run it on the first instance (after `pip install ortools`):
#   python finding_celebrities.py finding_celebrities.json

from ortools.sat.python import cp_model


def create_model(instance):
    """At a party, a celebrity is a person that everybody knows but that only
    knows other celebrities. Find the celebrities; at least one is present."""
    graph = instance["graph"]  # graph[i][j]: whether person i knows person j
    n_people = len(graph)      # the number of people at the party

    model = cp_model.CpModel()

    # celebrities[i] is true when person i is a celebrity
    celebrities = [model.new_bool_var(f"celebrities_{i}") for i in range(n_people)]
    # How many people are celebrities
    n_celebrities = model.new_int_var(1, n_people, "n_celebrities")

    # The number of celebrities is the number of people marked as celebrities.
    model.add(n_celebrities == sum(celebrities))

    for i in range(n_people):
        n_known_by = sum(graph[j][i] for j in range(n_people))  # how many people know person i
        n_knows = sum(graph[i])                                 # how many people person i knows
        # Someone that not everybody knows is no celebrity.
        if n_known_by != n_people:
            model.add(celebrities[i] == 0)
            continue
        # A celebrity knows every celebrity and only them, so it knows exactly n_celebrities people.
        model.add(n_knows == n_celebrities).only_enforce_if(celebrities[i])
        model.add(n_knows != n_celebrities).only_enforce_if(~celebrities[i])

    return model, {"celebrities": celebrities}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
