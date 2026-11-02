# session2_movie_scheduling: a PuLP (Python) model from DCP Rosetta.
# Download the `session2_movie_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python session2_movie_scheduling.py session2_movie_scheduling.json

import pulp


def create_model(instance):
    """An actor is offered movie projects, each with a first and last day of
    filming. Two projects whose filming days overlap cannot both be accepted:
    accept as many projects as possible."""
    movies = instance["movies"]  # movies[i]: the title, then the first and last day of filming, of offer i
    n_movies = len(movies)  # the number of movie offers

    problem = pulp.LpProblem("movie_scheduling", pulp.LpMaximize)

    # selected[i] is 1 when the actor accepts movie offer i, and 0 when not
    selected = [pulp.LpVariable(f"select_{i}", cat="Binary") for i in range(n_movies)]

    # The actor cannot accept two movies whose filming days overlap. Movies i and j
    # overlap when each one's last day comes after the other's first day.
    for i in range(n_movies):
        for j in range(i + 1, n_movies):
            if movies[i][2] > movies[j][1] and movies[j][2] > movies[i][1]:
                problem += selected[i] + selected[j] <= 1

    # Accept as many movies as possible, since every film pays the same fee.
    problem += pulp.lpSum(selected)

    return problem, {"selected_movies": selected}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
