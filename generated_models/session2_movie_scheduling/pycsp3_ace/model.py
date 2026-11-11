# session2_movie_scheduling: a PyCSP3 model from DCP Rosetta.
# Download the `session2_movie_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python session2_movie_scheduling.py session2_movie_scheduling.json

from pycsp3 import *


def create_model(instance):
    """An actor is offered the parts in several movie projects. Each offer has a first and a last
    day of filming, and the actor must be available for the whole period. Two jobs cannot be
    accepted when their intervals overlap. Find the largest set of jobs with no two of them in
    conflict."""
    movies = instance["movies"]  # movies[i]: [title, first day of filming, last day of filming] of film i
    n_movies = len(movies)
    first_day = [movie[1] for movie in movies]  # first_day[i]: the first day of filming of film i
    last_day = [movie[2] for movie in movies]   # last_day[i]: the last day of filming of film i

    # selected[i] is 1 when the actor accepts film i, and 0 when not.
    selected = VarArray(size=n_movies, dom={0, 1})

    # Films i and j conflict when they share a filming day (both end days included, so films that
    # only touch on one day conflict too; this reading of "overlap" is assumed).
    conflicts = [
        (i, j)
        for i in range(n_movies)
        for j in range(i + 1, n_movies)
        if first_day[i] <= last_day[j] and first_day[j] <= last_day[i]
    ]

    satisfy(
        # The accepted films do not overlap: of two conflicting films, at most one is accepted.
        [selected[i] + selected[j] <= 1 for i, j in conflicts],
    )

    # Accept as many films as possible, since each pays the same fee.
    maximize(Sum(selected))

    return {"selected_movies": selected}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
