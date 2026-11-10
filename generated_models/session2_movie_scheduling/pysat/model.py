# session2_movie_scheduling: a PySAT (Python) model from DCP Rosetta.
# Download the `session2_movie_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python session2_movie_scheduling.py session2_movie_scheduling.json

from pysat.formula import IDPool, WCNF


def create_model(instance):
    """An actor is offered movie projects, each with a first and last day of
    filming. Two projects whose filming periods overlap cannot both be accepted:
    accept as many projects as possible."""
    movies = instance["movies"]  # movies[i]: the title, first day and last day of filming of offer i
    n_movies = len(movies)  # the number of offers

    pool = IDPool()  # hands out the variable numbers

    # selected[i] is true when the actor accepts offer i
    selected = [pool.id(("selected", i)) for i in range(n_movies)]

    formula = WCNF()

    # Overlapping offers cannot both be accepted. Two offers overlap when each one
    # ends on or after the day the other starts.
    for i in range(n_movies):
        for j in range(i + 1, n_movies):
            if movies[i][2] >= movies[j][1] and movies[j][2] >= movies[i][1]:
                formula.append([-selected[i], -selected[j]])

    # Each offer pays the same fee. Turning one down costs 1, so the cheapest choice
    # accepts the most offers.
    for s in selected:
        formula.append([s], weight=1)

    # The objective in the problem's terms: the number of offers accepted (RC2's cost is the
    # number turned down).
    objective = [(1, s) for s in selected]

    return formula, {"selected_movies": selected}, objective


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs, objective = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
