# session3_kidney_exchange: a Gurobi (Python) model from DCP Rosetta.
# Download the `session3_kidney_exchange.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python session3_kidney_exchange.py session3_kidney_exchange.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Arrange kidney donations among n people on a waiting list, each donation only to a compatible person, so that as many people as possible receive a kidney: anyone who gives a kidney must receive one, and no one receives more than one."""
    n = instance["num_people"]  # the number of people, numbered 0 to n-1
    # compatible[i]: the people, numbered from 1, that person i can give a kidney to
    compatible = instance["compatible"]
    people = range(n)

    model = gp.Model("kidney_exchange")

    # transplants[i, j] is 1 when person i gives a kidney to person j, and 0 when not.
    transplants = model.addVars(people, people, vtype=GRB.BINARY, name="transplants")
    # A donation from i to j that is not compatible is ruled out: its upper bound is 0.
    for i in people:
        for j in people:
            if j + 1 not in compatible[i]:
                transplants[i, j].UB = 0

    # Each person gives at most one kidney (transplants.sum(i, "*") adds over the receivers j).
    # This is not in the statement: it is the setting that each person has one kidney to give.
    model.addConstrs((transplants.sum(i, "*") <= 1 for i in people), name="donate_once")
    # Each person receives at most one kidney (transplants.sum("*", i) adds over the donors).
    model.addConstrs((transplants.sum("*", i) <= 1 for i in people), name="receive_once")
    # Anyone who gives a kidney receives one: the kidneys person i gives are no more than those received.
    model.addConstrs((transplants.sum(i, "*") <= transplants.sum("*", i) for i in people),
                     name="gives_receives")

    # Objective: maximise the number of transplants, which is the number of people who receive a kidney.
    model.setObjective(transplants.sum(), GRB.MAXIMIZE)

    return model, {"transplants": [[transplants[i, j] for j in people] for i in people]}


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
