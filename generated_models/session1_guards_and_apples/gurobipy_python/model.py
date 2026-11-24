# session1_guards_and_apples: a Gurobi (Python) model from DCP Rosetta.
# Download the `session1_guards_and_apples.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python session1_guards_and_apples.py session1_guards_and_apples.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Guards and apples: how many apples the boy has before each gate, when each guard takes
    half of his apples plus one, and he ends with none after giving one to the girl."""
    gates = instance["num_gates"]  # num_gates: how many gates, and so guards, he passes

    model = gp.Model("guards_and_apples")

    # apples[i] is the number of apples he has before gate i (0-based), and apples[gates] is
    # the number after the last gate. The upper bound 100 is not in the statement: it is the
    # bound the reference uses.
    apples = model.addVars(gates + 1, lb=0, ub=100, vtype=GRB.INTEGER, name="apples")

    # After the last gate he has the one apple he gives to the girl, leaving none.
    model.addConstr(apples[gates] == 1, name="for_the_girl")

    # Each guard takes half of the apples plus one, so the apples before a gate are twice
    # the apples after it, plus two.
    model.addConstrs((apples[i - 1] == 2 * (apples[i] + 1) for i in range(1, gates + 1)),
                     name="gate")

    return model, {"apples": [apples[i] for i in range(gates + 1)]}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
