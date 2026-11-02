# session2_movie_scheduling: a Z3 (Python) model from DCP Rosetta.
# Download the `session2_movie_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python session2_movie_scheduling.py session2_movie_scheduling.json

import z3


def create_model(instance):
    """An actor is offered movie projects, each with a first and last day of
    filming. Two projects whose filming periods overlap cannot both be accepted:
    accept as many projects as possible."""
    movies = instance["movies"]  # movies[i]: the title, first day and last day of filming of movie i
    n_movies = len(movies)  # the number of movie offers

    # selected[i] is true when the actor accepts movie i
    selected = [z3.Bool(f"selected_{i}") for i in range(n_movies)]

    solver = z3.Optimize()

    # Two accepted movies never overlap: movies i and j overlap when each one
    # ends after the other starts.
    for i in range(n_movies):
        for j in range(i + 1, n_movies):
            if movies[i][2] > movies[j][1] and movies[j][2] > movies[i][1]:
                solver.add(z3.Not(z3.And(selected[i], selected[j])))

    # Earn as much as possible: every film pays the same fee, so this is the number of accepted movies.
    n_accepted = z3.Sum([z3.If(s, 1, 0) for s in selected])
    solver.maximize(n_accepted)

    return solver, {"selected_movies": selected}


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
