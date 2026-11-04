# huey_dewey_louie: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
# Run it (after `pip install pulp numpy`) with:
#   python huey_dewey_louie.py

import pulp


def create_model(instance):
    """Huey, Dewey and Louie are cub scouts questioned by their uncle, so they cannot lie:
    each of their statements is true. Who is guilty?"""
    # A satisfaction problem: the statements alone decide who is guilty.
    problem = pulp.LpProblem("huey_dewey_louie", pulp.LpMinimize)

    # Each variable is 1 when that nephew is guilty, and 0 when not.
    huey = pulp.LpVariable("huey", cat="Binary")
    dewey = pulp.LpVariable("dewey", cat="Binary")
    louie = pulp.LpVariable("louie", cat="Binary")

    # Huey: Dewey and Louie have an equal share in it; if one is guilty, so is the other.
    problem += dewey == louie
    # Dewey: if Huey is guilty, then so am I.
    problem += huey <= dewey
    # Louie: Dewey and I are not both guilty.
    problem += dewey + louie <= 1

    return problem, {"huey": huey, "dewey": dewey, "louie": louie}


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
