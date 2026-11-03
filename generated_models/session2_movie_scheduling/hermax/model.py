# session2_movie_scheduling: a hermax (Python) model from DCP Rosetta.
# Download the `session2_movie_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
# Then run it on the first instance (after `pip install hermax`):
#   python session2_movie_scheduling.py session2_movie_scheduling.json

from hermax.model import Model


def create_model(instance):
    """An actor is offered several movies, each filmed over a first and a last day.
    Two movies whose filming days overlap cannot both be taken. Choose the largest
    set of movies that can all be taken."""
    movies = instance["movies"]  # movies[i] = [title, first day of filming, last day of filming]
    n = len(movies)

    m = Model()
    # selected_movies[i] is true when the actor takes movie i
    selected_movies = m.bool_vector("selected_movies", n)

    # Two different movies whose filming periods share a day (each one ends on or after
    # the day the other starts) cannot both be taken.
    for i in range(n):
        for j in range(i + 1, n):
            if movies[i][2] >= movies[j][1] and movies[j][2] >= movies[i][1]:
                m &= (selected_movies[i] + selected_movies[j] <= 1)

    # Take as many movies as possible: the objective counts the movies left out,
    # so minimising it maximises the number taken.
    m.obj += sum(~selected_movies[i] for i in range(n))

    return m, {"selected_movies": selected_movies}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
