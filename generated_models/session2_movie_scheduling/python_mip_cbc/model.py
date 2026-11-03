# session2_movie_scheduling: a Python-MIP (Python) model from DCP Rosetta.
# Download the `session2_movie_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python session2_movie_scheduling.py session2_movie_scheduling.json

import mip


def create_model(instance):
    """An actor is offered movie projects, each with a first and last day of
    filming. The actor must be free for the whole filming period, so two projects
    whose periods overlap cannot both be accepted. Accept as many projects as
    possible."""
    movies = instance["movies"]  # movies[i]: [title, first day, last day] of filming for offer i
    n_movies = len(movies)  # the number of offers
    starts = [movie[1] for movie in movies]  # starts[i]: the first day of filming of offer i
    ends = [movie[2] for movie in movies]  # ends[i]: the last day of filming of offer i

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # selected[i] is 1 when the actor accepts offer i, and 0 when not
    selected = [model.add_var(f"selected_{i}", var_type=mip.BINARY) for i in range(n_movies)]

    # On each day, at most one accepted offer may be filming. Days are whole,
    # so two offers overlap exactly when they share a filming day.
    for day in range(min(starts, default=0), max(ends, default=0) + 1):
        filming = [selected[i] for i in range(n_movies) if starts[i] <= day <= ends[i]]  # the offers filming on this day
        if len(filming) >= 2:  # a day with fewer than two offers gives no restriction
            model.add_constr(mip.xsum(filming) <= 1)

    # Accept as many offers as possible, since every project pays the same fee.
    model.objective = mip.xsum(selected)

    return model, {"selected_movies": selected}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
