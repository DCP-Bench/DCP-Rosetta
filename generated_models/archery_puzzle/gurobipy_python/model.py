# archery_puzzle: a Gurobi (Python) model from DCP Rosetta.
# Download the `archery_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python archery_puzzle.py archery_puzzle.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """A young archer shoots arrows at targets, each worth a set number of points, using as
    many arrows as she pleases. Choose how many arrows hit each target so that the total
    score comes as close as possible to the target score."""
    targets = instance["targets"]  # targets[i]: the points for one arrow hitting target i
    goal = instance["target_score"]  # the target score she aims for
    rings = range(len(targets))

    model = gp.Model("archery_puzzle")

    # hits[i] is how many arrows hit target i. The upper bound goal is not from the statement:
    # it keeps the variables finite, and the reference model uses it.
    hits = model.addVars(rings, lb=0, ub=goal, vtype=GRB.INTEGER, name="hits")

    # score is the total points of all the arrows. The upper bound 2 * goal is not from the
    # statement: it keeps the variable finite, and the reference model uses it.
    score = model.addVar(lb=0, ub=2 * goal, vtype=GRB.INTEGER, name="score")
    # The total score is the points of each target times the arrows that hit it.
    model.addConstr(score == gp.quicksum(targets[i] * hits[i] for i in rings), name="score")

    # deviation is how far the total score is from the target score. Its upper bound 2 * goal is
    # not from the statement. Two lower bounds suffice because deviation is minimised: at the
    # optimum it equals |goal - score|.
    deviation = model.addVar(lb=0, ub=2 * goal, vtype=GRB.INTEGER, name="deviation")
    # deviation is at least the shortfall and at least the excess of the score over the target.
    model.addConstr(deviation >= goal - score, name="below_goal")
    model.addConstr(deviation >= score - goal, name="above_goal")

    # Minimise the distance between the total score and the target score.
    model.setObjective(deviation, GRB.MINIMIZE)

    return model, {"hits": [hits[i] for i in rings]}


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
