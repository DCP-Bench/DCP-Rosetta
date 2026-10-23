from hermax.model import Model


def build(instance):
    movies = instance["movies"]
    # Each movie is [title, first day, last day]; the title is not used in the model.
    starts = [int(movie[1]) for movie in movies]
    ends = [int(movie[2]) for movie in movies]
    n = len(movies)

    m = Model()
    # selected[i] is true when movie i is accepted.
    selected = m.bool_vector("selected", n)

    # Two movies cannot both be accepted when their filming periods overlap:
    # they overlap when each one starts before the other ends.
    for i in range(n):
        for j in range(i + 1, n):
            if starts[i] <= ends[j] and starts[j] <= ends[i]:
                m &= (~selected[i] | ~selected[j])

    # Maximise the number of movies accepted: each movie left out costs one.
    for i in range(n):
        m.obj[1] += selected[i]

    return m, {"selected_movies": selected}
