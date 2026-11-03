# session2_movie_scheduling: a Choco-solver (Python) model from DCP Rosetta.
# Download the `session2_movie_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python session2_movie_scheduling.py session2_movie_scheduling.json

from pychoco.model import Model


def create_model(instance):
    """An actor is offered movie projects, each with a first and last day of
    filming, and must be available on every day of it. Pick the largest set of
    projects whose filming periods do not share a day."""
    movies = instance["movies"]  # movies[i]: [title, first day, last day] of filming for movie i
    n_movies = len(movies)       # the number of movie offers

    model = Model()

    # selected_movies[i] is true when the actor accepts movie i
    selected_movies = [model.boolvar(name=f"selected_{i}") for i in range(n_movies)]

    # Overlapping movies cannot both be accepted.
    for i in range(n_movies):
        for j in range(i + 1, n_movies):
            if movies[i][2] >= movies[j][1] and movies[j][2] >= movies[i][1]:
                model.sum([selected_movies[i], selected_movies[j]], "<=", 1).post()

    # The number of accepted movies. The actor maximises it, since every film pays the same fee.
    n_selected = model.intvar(0, n_movies, name="n_selected")
    model.sum(selected_movies, "=", n_selected).post()

    return model, {"selected_movies": selected_movies}, {"objective": n_selected, "maximize": True}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
