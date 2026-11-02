"""Movie scheduling: accept the largest set of movies whose filming periods do not overlap."""
import hexaly.optimizer as hx


def build(instance):
    movies = instance["movies"]  # [name, first day, last day]
    n = len(movies)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # selected_movies[i] = 1 if movie i is accepted
    selected_movies = [model.bool() for _ in range(n)]

    # Two movies whose periods share a day (the last day counts) cannot both be accepted
    for a in range(n):
        for b in range(a + 1, n):
            if movies[a][1] <= movies[b][2] and movies[b][1] <= movies[a][2]:
                model.constraint(selected_movies[a] + selected_movies[b] <= 1)

    # Every movie pays the same fee, so maximise the number of movies
    model.maximize(model.sum(selected_movies))
    return optimizer, {"selected_movies": selected_movies}
