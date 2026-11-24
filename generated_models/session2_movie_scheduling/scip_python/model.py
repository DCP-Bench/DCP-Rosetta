# session2_movie_scheduling: a SCIP (Python) model from DCP Rosetta.
# Download the `session2_movie_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python session2_movie_scheduling.py session2_movie_scheduling.json

from itertools import combinations

from pyscipopt import Model, quicksum


def create_model(instance):
    """An actor is offered film jobs, each with a first and a last day of filming,
    and must be available on every day from the first to the last, both included.
    Two jobs whose filming days share a day cannot both be taken. Choose the
    largest set of jobs that clash with none of the others."""
    movies = instance["movies"]  # movies[i]: [title, first filming day, last filming day] of offer i

    model = Model("movie_scheduling")

    # selected[i] is 1 when the actor accepts offer i, and 0 when not
    selected = [model.addVar(f"selected_{i}", vtype="B") for i in range(len(movies))]

    # Two offers clash when their filming days share a day. Each offer runs from
    # its first to its last day, so the two overlap exactly when each one starts
    # no later than the other ends. Two clashing offers cannot both be accepted.
    for i, j in combinations(range(len(movies)), 2):
        first_i, last_i = movies[i][1:]
        first_j, last_j = movies[j][1:]
        if first_i <= last_j and first_j <= last_i:
            model.addCons(selected[i] + selected[j] <= 1)

    # The objective counts the accepted offers, so the actor takes as many jobs as possible.
    model.setObjective(quicksum(selected), "maximize")

    return model, {"selected_movies": selected}


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
