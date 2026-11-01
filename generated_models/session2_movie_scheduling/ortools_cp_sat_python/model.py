# session2_movie_scheduling: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `session2_movie_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
# Then run it on the first instance (after `pip install ortools`):
#   python session2_movie_scheduling.py session2_movie_scheduling.json

from ortools.sat.python import cp_model


def create_model(instance):
    """An actor is offered movie projects, each with a first and last day of
    filming. Two projects whose intervals overlap cannot both be accepted: accept
    as many projects as possible."""
    movies = instance["movies"]  # movies[i]: [title, first day, last day] of filming for movie i
    n_movies = len(movies)  # the number of movies

    model = cp_model.CpModel()

    # selected[i] is true when the actor accepts movie i
    selected = [model.new_bool_var(f"selected_{i}") for i in range(n_movies)]

    # No two accepted movies overlap: movies i and j overlap when each ends
    # after the other starts.
    for i in range(n_movies):
        for j in range(i + 1, n_movies):
            if movies[i][2] > movies[j][1] and movies[j][2] > movies[i][1]:
                model.add_at_most_one([selected[i], selected[j]])

    # Accept as many movies as possible, since every film pays the same fee.
    model.maximize(sum(selected))

    return model, {"selected_movies": selected}


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
