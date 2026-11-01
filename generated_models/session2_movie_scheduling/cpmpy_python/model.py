# session2_movie_scheduling: a CPMpy model from DCP Rosetta.
# Download the `session2_movie_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python session2_movie_scheduling.py session2_movie_scheduling.json

import cpmpy as cp


def create_model(instance):
    """An actor is offered n movie projects, each with a first and last day of
    filming. Two projects whose intervals overlap cannot both be accepted: accept
    as many projects as possible."""
    movies = instance["movies"]  # movies[i]: [title, first day, last day] of filming
    n_movies = len(movies)

    # selected[i] is true when the actor accepts movie i
    selected = cp.boolvar(shape=n_movies, name="selected_movies")

    model = cp.Model()
    # No two accepted movies overlap: movies i and j overlap when each ends
    # after the other starts.
    for i in range(n_movies):
        for j in range(i + 1, n_movies):
            if movies[i][2] > movies[j][1] and movies[j][2] > movies[i][1]:
                model.add(selected[i] + selected[j] <= 1)
    # Accept the largest number of movies (every film pays the same fee).
    model.maximize(cp.sum(selected))

    return model, {"selected_movies": selected}


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
