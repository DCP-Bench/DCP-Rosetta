# session2_movie_scheduling: a Gurobi (Python) model from DCP Rosetta.
# Download the `session2_movie_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python session2_movie_scheduling.py session2_movie_scheduling.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """An actor is offered films, each with a filming period from its first to its last day,
    and must be available for the whole period. Accept as many offers as possible, so that
    no two accepted periods overlap."""
    movies = instance["movies"]  # movies[i] is [title, first day, last day] of offer i
    films = range(len(movies))

    model = gp.Model("movie_scheduling")

    # selected[i] is 1 when offer i is accepted.
    selected = model.addVars(films, vtype=GRB.BINARY, name="selected_movies")

    # Two offers overlap when their filming periods share at least one day; overlapping
    # offers cannot both be accepted.
    model.addConstrs(
        (selected[i] + selected[j] <= 1
         for i in films for j in films
         if j > i and movies[i][2] >= movies[j][1] and movies[j][2] >= movies[i][1]),
        name="overlap",
    )

    # Objective: the number of films accepted, since each pays the same fee.
    model.setObjective(selected.sum(), GRB.MAXIMIZE)

    # selected_movies[i] is 1 when offer i is accepted, in the order of the input list.
    return model, {"selected_movies": [selected[i] for i in films]}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.Params.MIPGap = 0  # prove the optimum; the default stops within 0.01% of it
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a proven optimum
        print("Objective value:", round(model.ObjVal))
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
