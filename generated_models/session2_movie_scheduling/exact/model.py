# session2_movie_scheduling: an Exact (Python) model from DCP Rosetta.
# Download the `session2_movie_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python session2_movie_scheduling.py session2_movie_scheduling.json

from exact import Exact


def create_model(instance):
    """An actor is offered movie projects, each with a first and last day of
    filming. Two projects whose intervals overlap cannot both be accepted: accept
    as many projects as possible."""
    movies = instance["movies"]  # the movie offers, each with its first and last day of filming
    n_movies = len(movies)  # the number of offers

    solver = Exact()

    # Exact identifies its variables by name.
    # selected[i] is 1 when the actor accepts movie i, and 0 when not
    selected = [f"selected_{i}" for i in range(n_movies)]
    for name in selected:
        solver.addVariable(name, 0, 1)

    # Two accepted movies may not share a day of filming: movies i and j overlap
    # when each one ends on or after the day the other starts.
    for i in range(n_movies):
        for j in range(i + 1, n_movies):
            if movies[i][2] >= movies[j][1] and movies[j][2] >= movies[i][1]:
                solver.addConstraint([(1, selected[i]), (1, selected[j])], False, 0, True, 1)

    # Accept as many movies as possible, since each film pays the same fee.
    solver.setObjective([(1, name) for name in selected], minimize=False)

    return solver, {"selected_movies": selected}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
